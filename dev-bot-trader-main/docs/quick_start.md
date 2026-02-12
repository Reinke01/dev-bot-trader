# Quick Start

Backend (API):

```bash
# From repo root
E:/workspace/dev-bot-trader-main.ziporiginal/.venv/Scripts/python.exe -m uvicorn src.api.main:app --reload --app-dir src --port 8000
```

Frontend (Dashboard):

```bash
cd devbot-trader-dashboard
npm run dev -- --port 8080
```

.env (project root):

```dotenv
BYBIT_API_KEY=...
BYBIT_API_SECRET=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
GOOGLE_API_KEY=...
```

Frontend `.env` (devbot-trader-dashboard/.env):

```dotenv
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```
