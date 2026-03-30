"""
Configurações do Worker unificado (ARQ) para o Free Tier.
Roda todas as filas no mesmo processo:
  arq app.workers.main.WorkerSettings
"""
from app.core.queues import redis_settings
from app.core.logging import setup_logging, logger
from app.workers.inbound import process_inbound_message, handle_dlq_inbound
from app.workers.outbound import process_outbound_message

async def startup(ctx):
    setup_logging()
    logger.info("worker.startup", queue="unified")

async def shutdown(ctx):
    logger.info("worker.shutdown", queue="unified")

class WorkerSettings:
    redis_settings = redis_settings
    on_startup = startup
    on_shutdown = shutdown
    functions = [
        process_inbound_message,
        process_outbound_message,
        handle_dlq_inbound
    ]
    max_tries = 3                # PRD: attempts: 3
    job_timeout = 300
    keep_result = 86400          # TTL para completed
    keep_result_forever = False  # PRD: removeOnComplete
