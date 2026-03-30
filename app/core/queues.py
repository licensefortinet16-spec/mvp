from arq.connections import RedisSettings
from app.core.config import settings

# Parse redis://localhost:6379 to host and port
# For simplicity in MVP, we split the standard URL
_redis_host = settings.redis_url.split("://")[1].split(":")[0]
_redis_port = int(settings.redis_url.split("://")[1].split(":")[1].split("/")[0])

# Configurações do Redis para as filas (arq)
redis_settings = RedisSettings(
    host=_redis_host,
    port=_redis_port,
    conn_retries=5,
    conn_timeout=5.0
)

# Constantes com os nomes das filas solicitadas no MVP
QUEUE_INBOUND = "inbound_messages"
QUEUE_OUTBOUND = "outbound_messages"
QUEUE_DLQ = "dlq_inbound"
