"""
Configurações dos Workers (ARQ).
Para rodar cada fila em um processo separado:
  arq app.workers.main.WorkerInbound
  arq app.workers.main.WorkerOutbound
  arq app.workers.main.WorkerDLQ
"""
from app.core.queues import redis_settings, QUEUE_INBOUND, QUEUE_OUTBOUND, QUEUE_DLQ
from app.core.logging import setup_logging, logger
from app.workers.inbound import process_inbound_message, handle_dlq_inbound
from app.workers.outbound import process_outbound_message

async def startup(ctx):
    setup_logging()
    logger.info("worker.startup", queue=ctx["queue_name"])

async def shutdown(ctx):
    logger.info("worker.shutdown", queue=ctx["queue_name"])

class BaseWorkerSettings:
    redis_settings = redis_settings
    on_startup = startup
    on_shutdown = shutdown
    max_tries = 3                # PRD: attempts: 3
    job_timeout = 300
    keep_result = 86400          # TTL para completed
    keep_result_forever = False  # PRD: removeOnComplete

class WorkerInbound(BaseWorkerSettings):
    queue_name = QUEUE_INBOUND
    functions = [process_inbound_message]

class WorkerOutbound(BaseWorkerSettings):
    queue_name = QUEUE_OUTBOUND
    functions = [process_outbound_message]

class WorkerDLQ(BaseWorkerSettings):
    queue_name = QUEUE_DLQ
    functions = [handle_dlq_inbound]
