import redis.asyncio as redis
from arq import create_pool
from app.core.config import settings
from app.core.queues import redis_settings

# Cliente genérico para o FastAPI usar (deduplicação, etc)
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

# Pool do ARQ para enfileirar jobs a partir do FastAPI
arq_pool = None

async def get_arq_pool():
    global arq_pool
    if arq_pool is None:
        arq_pool = await create_pool(redis_settings)
    return arq_pool
