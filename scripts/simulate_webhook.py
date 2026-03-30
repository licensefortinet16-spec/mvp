import asyncio
import httpx
import hmac
import hashlib
import json
import time

from app.core.config import settings

async def simulate_webhook():
    print("🚀 Simulando recebimento de mensagem (Webhook) localmente...")
    
    url = "http://localhost:8000/webhook"
    
    # Payload similar ao enviado pela Meta
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": settings.meta_waba_id,
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "11111111111",
                        "phone_number_id": settings.meta_phone_number_id
                    },
                    "contacts": [{
                        "profile": {"name": "Usuário Teste"},
                        "wa_id": "5511999999999"
                    }],
                    "messages": [{
                        "from": "5511999999999",
                        "id": f"wamid.{int(time.time())}",
                        "timestamp": str(int(time.time())),
                        "text": {"body": "Teste de mensagem do script local!"},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    body_bytes = json.dumps(payload).encode("utf-8")
    
    # Gera a assinatura HMAC SHA-256 usando o META_WEBHOOK_SECRET
    secret = settings.meta_webhook_secret.encode("utf-8")
    signature = hmac.new(secret, body_bytes, hashlib.sha256).hexdigest()
    
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": f"sha256={signature}"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, content=body_bytes, headers=headers)
            print(f"✅ Webhook respondeu com status {response.status_code}")
            print(f"Resposta: {response.json()}")
        except Exception as e:
            print(f"❌ Erro ao conectar no webhook local. A API está rodando na porta 8000? Erro: {e}")

if __name__ == "__main__":
    asyncio.run(simulate_webhook())
