# Arquitetura (texto)

Visão geral

Este monorepo contém dois aplicativos principais:

- Backend (FastAPI): responsável por endpoints REST e WebSocket, orquestração dos bots de trading e integração com corretoras (Bybit), além do envio de notificações (Telegram).
- Frontend (Vite + React): painel de controle, exibindo status dos bots, formulário de start/stop e gráficos de candles.

Responsabilidades
- Backend:
  - Expor endpoints: `/health`, `/api/v1/candles`, `/api/v1/bot/*`, `/api/v1/ws/logs/*`.
  - Gerenciar ciclos de vida dos bots (start/stop/status).
  - Integrar com APIs externas (Bybit, Telegram).
  - Implementar rate-limiting/backoff para chamadas à corretora.

- Frontend:
  - Consumir `VITE_API_BASE_URL` e `VITE_WS_BASE_URL` (dev por padrão `http://localhost:8000` / `ws://localhost:8000`).
  - Mostrar painel de bots, logs via WebSocket e charts via chamadas `/api/v1/candles`.

Observações de implantação
- Projetos são independentes e podem ser containerizados separadamente.
- Comunicação backend/frontend é via HTTP/WS; reverso proxy (NGINX/Caddy) recomendado para TLS.
