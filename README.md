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

## Deploy (Railway - Free Tier)

### 1. Criar o Projeto
- No painel, crie um novo projeto
- Adicione as instâncias gerenciadas do PostgreSQL e Redis (`New > Database > PostgreSQL`, `New > Database > Redis`)
- Conecte seu repositório GitHub (`licensefortinet16-spec/mvp`). O Railway vai identificar o `Dockerfile` e `railway.toml`.

### 2. Configuração Unificada
O projeto foi ajustado para rodar a **API Web** e os **Workers ARQ** no mesmo container via `start.sh` (economizando serviços no plano Free). Você **não precisa** criar serviços adicionais de worker no painel.

### 3. Variáveis de Ambiente
Na aba "Variables" do seu serviço principal conectado ao GitHub, adicione todas as variáveis do seu `.env` local.
- `DATABASE_URL` = (Referencie do serviço Postgres, clique em "Reference" -> `${{Postgres.DATABASE_URL}}`)
- `REDIS_URL` = (Referencie do serviço Redis -> `${{Redis.REDIS_URL}}`)

### 4. Últimos Ajustes
- Rode as migrations: No terminal interno do container no painel do Railway, digite `alembic upgrade head`.
- Crie o seu logista de teste: No terminal interno, digite `python3 scripts/seed.py`.
- Copie o domínio gerado pelo Railway (ex: `https://seu-dominio-railway.app/webhook`) e cadastre na Meta for Developers, usando o `META_WEBHOOK_SECRET` que você colocou nas Variáveis.
