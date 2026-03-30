import hmac
import hashlib
from app.core.config import settings

def verify_meta_signature(payload: bytes, signature_header: str) -> bool:
    """
    Verifica se a assinatura HMAC recebida no X-Hub-Signature-256 é válida,
    garantindo que o payload veio genuinamente da Meta.
    """
    if not signature_header or not signature_header.startswith("sha256="):
        return False
        
    signature = signature_header.split("sha256=")[1]
    secret = settings.meta_webhook_secret.encode("utf-8")
    
    expected_signature = hmac.new(
        secret,
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)
