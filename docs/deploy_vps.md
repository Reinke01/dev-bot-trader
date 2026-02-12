# Deploy (VPS) - Docker Compose

Objetivo: subir backend FastAPI e frontend Vite em uma VPS usando Docker Compose e um serviço `systemd` simples.

Arquivos/serviços esperados
- backend: imagem Docker construída a partir de `dev-bot-trader-main/` expondo `8000` (uvicorn)
- frontend: build estático servido por `nginx` na porta `8080` ou servido pelo `vite` em dev

Variáveis de ambiente (não comitar em .env):
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
- BYBIT_API_KEY / BYBIT_API_SECRET
- POLL_INTERVAL_SECONDS

Exemplo `docker-compose.yml` (sintético):

```yaml
version: '3.8'
services:
  backend:
    build: ./dev-bot-trader-main
    restart: unless-stopped
    env_file:
      - ./secrets/backend.env   # NÃO commitar este arquivo
    ports:
      - "8000:8000"
    command: python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --app-dir src --reload

  frontend:
    build: ./devbot-trader-dashboard
    restart: unless-stopped
    ports:
      - "8080:80"   # se servir via nginx

# Volumes, networks e secrets podem ser adicionados conforme necessário
```

systemd (opcional): crie unidade que execute `docker-compose -f /path/to/docker-compose.yml up -d` e monitore o serviço.

Segurança
- Nunca comite arquivos `*.env` ou `secrets/*`.
- Use `aws ssm`, `vault` ou variáveis de ambiente do provedor para armazenar segredos.

Checklist de deploy manual (VPS)
1. Copiar código para VPS (via git) — remova qualquer `.env` local antes.
2. Criar `secrets/backend.env` no servidor com as variáveis necessárias.
3. Rodar `docker-compose up -d --build`.
4. Conferir logs: `docker-compose logs -f backend`.
5. Testar: `curl http://127.0.0.1:8000/health`.

Notas
- Este documento é um guia inicial. Ajuste Dockerfile(s) para garantir builds reproduzíveis e que dependências nativas (e.g., libs de sistema) estejam instaladas.
