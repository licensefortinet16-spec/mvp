import os
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.logging import setup_logging, logger
from app.core.redis import get_arq_pool, redis_client
from app.routes import webhook


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("app.startup", env=os.getenv("APP_ENV", "development"))
    # Inicializa pool do ARQ
    await get_arq_pool()
    yield
    # Cleanup
    logger.info("app.shutdown")
    pool = await get_arq_pool()
    await pool.close()
    await redis_client.aclose()


app = FastAPI(
    title="WhatsApp Business API MVP",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(webhook.router, prefix="/webhook", tags=["webhook"])


@app.get("/health")
async def health():
    return {"status": "ok"}
