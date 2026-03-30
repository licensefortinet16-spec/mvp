import httpx
from app.core.config import settings
from app.core.logging import logger

async def send_whatsapp_message(to: str, payload_type: str, content: dict) -> tuple[int, dict]:
    """
    Envia uma mensagem via Meta Graph API.
    Retorna uma tupla (status_code, response_json).
    """
    url = f"{settings.meta_graph_url}/{settings.meta_phone_number_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {settings.meta_access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": payload_type,
        payload_type: content
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            try:
                resp_data = response.json()
            except Exception:
                resp_data = {"error": "Invalid JSON response from Meta"}
                
            return response.status_code, resp_data
            
    except httpx.RequestError as exc:
        logger.error("meta.api.request_error", error=str(exc))
        # Simulamos um 503 para que o worker saiba que foi falha de rede e faça retry
        return 503, {"error": "Network request failed"}
        
    return 500, {"error": "Unknown error during API request"}
