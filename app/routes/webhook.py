from fastapi import APIRouter, Request, HTTPException, Query, Header
from app.core.config import settings
from app.core.logging import logger
from app.core.security import verify_meta_signature
from app.core.redis import redis_client, get_arq_pool

router = APIRouter()


@router.get("")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """Verificação do webhook pela Meta (GET)."""
    if hub_mode == "subscribe" and hub_verify_token == settings.meta_webhook_secret:
        logger.info("webhook.verified")
        return int(hub_challenge)
    logger.warning("webhook.verify_failed", token=hub_verify_token)
    raise HTTPException(status_code=403, detail="Forbidden")


@router.post("")
async def receive_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(None, alias="X-Hub-Signature-256")
):
    """Recebimento de mensagens WhatsApp (POST) com validação HMAC."""
    raw_body = await request.body()
    
    if not verify_meta_signature(raw_body, x_hub_signature_256):
        logger.warning("webhook.signature_invalid", signature=x_hub_signature_256)
        raise HTTPException(status_code=403, detail="Invalid signature")
        
    try:
        body = await request.json()
    except Exception:
        logger.error("webhook.invalid_json")
        raise HTTPException(status_code=400, detail="Invalid JSON")
        
    logger.info("webhook.received", payload=body)
    
    # Processamento e Deduplicação (Etapa 4 / 5 do PRD Webhook)
    arq_pool = await get_arq_pool()
    
    if "entry" in body:
        for entry in body["entry"]:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                waba_id = value.get("metadata", {}).get("phone_number_id")
                
                # Ignorar status updates por enquanto (MVP é só mensagens in/out)
                if "messages" not in value:
                    continue
                    
                for message in value.get("messages", []):
                    msg_id = message.get("id")
                    if not msg_id:
                        continue
                        
                    # Deduplicação no Redis
                    dedup_key = f"dedup:msg:{msg_id}"
                    is_duplicate = await redis_client.set(dedup_key, "1", ex=86400, nx=True)
                    
                    if not is_duplicate:
                        logger.warning("webhook.message_duplicated", message_id=msg_id)
                        continue
                        
                    # Enfileirar processo
                    logger.info("webhook.enqueued", message_id=msg_id)
                    await arq_pool.enqueue_job(
                        "process_inbound_message",
                        payload={"waba_id": waba_id, "message": message}
                    )
    
    return {"status": "received"}
