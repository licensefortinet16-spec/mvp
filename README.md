# MVP WhatsApp Business API + Railway

Backend para receber e enviar mensagens via WhatsApp Business API (Meta), com filas Redis, banco PostgreSQL e deploy no Railway.

## Estrutura

```
app/
  core/        # config, logging
  routes/      # webhook (GET + POST)
  services/    # cliente Meta Graph API
  workers/     # inbound e outbound
  models/      # SQLAlchemy models
  main.py      # FastAPI entrypoint
migrations/    # Alembic
scripts/       # utilitários
docker-compose.yml  # Redis + PostgreSQL locais
```

## Setup Local

### 1. Clone e configure o .env

```bash
cp .env.example .env
# edite .env com seus tokens da Meta
```

### 2. Suba os containers

```bash
docker compose up -d
```

### 3. Crie o venv e instale dependências

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Rode a aplicação

```bash
uvicorn app.main:app --reload
```

### 5. Teste o health check

```bash
curl http://localhost:8000/health
```

## Deploy (Railway)

### 1. Criar o Projeto
- No painel, crie um novo projeto
- Adicione as instâncias gerenciadas do PostgreSQL e Redis (`New > Database > PostgreSQL`, `New > Database > Redis`)
- Conecte seu repositório GitHub para o Web/API. Railway vai buildar via Dockerfile e rodar o `railway.toml`.

### 2. Configurar Workers
O projeto exige 3 workers simultâneos. No Railway, adicione 3 **Empty Services** e aponte para o mesmo repositório, mas mude o **Start Command** deles:

- Worker Inbound: `arq app.workers.main.WorkerInbound`
- Worker Outbound: `arq app.workers.main.WorkerOutbound`
- Worker DLQ: `arq app.workers.main.WorkerDLQ`

### 3. Variáveis de Ambiente
Copie todas as variáveis do `.env` para todos os 4 serviços (API + os 3 Workers), ajustando o `DATABASE_URL` e `REDIS_URL` para as internas do Railway (`${{Redis.REDIS_URL}}`, etc).

### 4. Últimos Ajustes
- Rode as migrations: `alembic upgrade head` no shell do serviço Web
- Rode o seeder: `python3 scripts/seed.py` para criar o seu tenant com WABA_ID via shell
- Mude a URL na tela de WhatsApp Settings da Meta for Developers para: `https://seu-dominio-railway.app/webhook`
