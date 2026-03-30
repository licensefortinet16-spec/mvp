#!/bin/bash
set -e

echo "Iniciando Worker ARQ unificado em background..."
arq app.workers.main.WorkerSettings &
WORKER_PID=$!

echo "Iniciando FastAPI Web Server..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} &
WEB_PID=$!

# Aguarda qualquer um dos processos encerrar para derrubar o container se houver problema
wait -n $WORKER_PID $WEB_PID

exit $?
