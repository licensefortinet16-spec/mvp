import asyncio
import random
from arq import Retry
from app.core.logging import logger
from app.services.meta import send_whatsapp_message
from app.core.redis import get_arq_pool


async def process_outbound_message(ctx, payload: dict):
    """
    Processa mensagens a serem enviadas pela Graph API.
    A Etapa 5 exige lógica de retry com status code e backoff iterativo.
    """
    job_id = ctx.get("job_id")
    job_try = ctx.get("job_try", 1)
    
    to = payload.get("to")
    msg_type = payload.get("type", "text")
    content = {"body": payload.get("text")} if msg_type == "text" else payload.get("content", {})
    
    logger.info("worker.outbound.started", job_id=job_id, attempt=job_try, to=to)
    
    status_code, response_data = await send_whatsapp_message(to, msg_type, content)
    
    # Sucesso
    if 200 <= status_code < 300:
        logger.info("worker.outbound.success", job_id=job_id, status=status_code)
        return {"status": "sent", "type": "outbound", "api_response": response_data}
        
    # Lógica de falha: erro 131030 (número não registrado - PRD) -> sem retry, move DLQ
    error_data = response_data.get("error", {})
    error_code = error_data.get("code")
    error_subcode = error_data.get("error_subcode")
    
    if error_code == 131030 or error_subcode == 131030:
        logger.error("worker.outbound.number_not_registered", phone=to)
        arq_pool = await get_arq_pool()
        await arq_pool.enqueue_job(
            "handle_dlq_inbound", # Reusando a mesma DLQ function para simplificar logging MVP
            payload=payload,
            error_msg="Error 131030: Number not registered",
            _queue_name=QUEUE_DLQ
        )
        return {"status": "failed", "reason": "131030"}

    # Retry para falhas temporárias (5xx, timeouts) ou Rate Limits (429)
    if status_code >= 500 or status_code == 429:
        if job_try >= 3:
            logger.error("worker.outbound.max_retries", job_id=job_id, status=status_code)
            arq_pool = await get_arq_pool()
            await arq_pool.enqueue_job(
                "handle_dlq_inbound",
                payload=payload,
                error_msg=f"Max retries reached. Last status: {status_code}"
            )
            return {"status": "failed", "reason": "max_retries"}
            
        # Backoff exponencial com jitter (PRD: base 1000ms * 2^attempt + jitter)
        base_delay = 1.0 * (2 ** job_try)
        jitter = random.uniform(0.1, 0.5)
        retry_delay = base_delay + jitter
        
        logger.warning("worker.outbound.retry", delay=retry_delay, status=status_code)
        raise Retry(defer=retry_delay)
        
    # Falhas 4xx irreversíveis sem retry (ex: 400 Bad Request)
    logger.error("worker.outbound.fatal_error", status=status_code, response=response_data)
    arq_pool = await get_arq_pool()
    await arq_pool.enqueue_job(
        "handle_dlq_inbound",
        payload=payload,
        error_msg=f"Fatal 4xx error: {status_code}"
    )
    return {"status": "failed", "reason": f"fatal_{status_code}"}
