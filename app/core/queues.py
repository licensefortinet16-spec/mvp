from arq.connections import RedisSettings
from app.core.config import settings

# Parse nativo da URL do Redis para configuração do ARQ
redis_settings = RedisSettings.from_dsn(settings.redis_url)

# Constantes obsoletas (mantidas só por segurança se houver algum import antigo)
QUEUE_INBOUND = "inbound_messages"
QUEUE_OUTBOUND = "outbound_messages"
QUEUE_DLQ = "dlq_inbound"
