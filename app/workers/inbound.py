from arq import Retry
from app.core.logging import logger
from app.core.redis import redis_client, get_arq_pool

async def process_inbound_message(ctx, payload: dict):
    """
    Processa mensagens recebidas do Webhook.
    """
    job_id = ctx.get("job_id")
    job_try = ctx.get("job_try", 1)
    
    logger.info("worker.inbound.started", job_id=job_id, attempt=job_try)
    
    try:
        waba_id = payload.get("waba_id")
        message = payload.get("message", {})
        
        user_phone = message.get("from")
        msg_id = message.get("id")
        
        # O text.body existe apenas para tipo texto
        msg_type = message.get("type")
        body = message.get("text", {}).get("body", "") if msg_type == "text" else f"[{msg_type}]"
        
        logger.info("worker.inbound.extracted", phone=user_phone, msg_id=msg_id, body=body)
        
        # 1. Atualiza chave de sessão
        session_key = f"session:{waba_id}:{user_phone}"
        await redis_client.set(session_key, "active", ex=86400)
        
        # 2. Validação da janela de 24h para envio de texto livre
        # Aqui, como acabamos de setar, sempre será True.
        # Em fluxos reais assíncronos (Ex: trigger do painel), isso é checado de forma isolada.
        is_active = await redis_client.exists(session_key)
        if not is_active:
            logger.warning("worker.inbound.session_expired", phone=user_phone)
            # Não envia a mensagem se fora da janela
            return {"status": "ignored", "reason": "outside_24h_window"}
        
        # 3. Enfileira resposta de echo
        arq_pool = await get_arq_pool()
        await arq_pool.enqueue_job(
            "process_outbound_message",
            payload={
                "waba_id": waba_id,
                "to": user_phone,
                "text": f"Echo: {body}"
            }
        )
        
        logger.info("worker.inbound.completed", job_id=job_id)
        return {"status": "processed", "type": "inbound"}

    except Exception as e:
        logger.error("worker.inbound.error", error=str(e), exc_info=True)
        # Se for a última tentativa (max_tries=3 no WorkerSettings), movemos para a DLQ
        if job_try >= 3:
            arq_pool = await get_arq_pool()
            await arq_pool.enqueue_job(
                "handle_dlq_inbound",
                payload=payload,
                error_msg=str(e)
            )
        raise Retry(defer=1)  # Tenta novamente em 1s (backoff simples)

async def handle_dlq_inbound(ctx, payload: dict, error_msg: str):
    """Dead Letter Queue para mensagens de inbound que falharam após 3 tentativas."""
    logger.error("worker.dlq_inbound.received", payload=payload, error=error_msg)
    return {"status": "dlq_logged"}
