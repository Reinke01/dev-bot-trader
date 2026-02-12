# Quickstart (local development)

Prerequisites:
- Windows PowerShell
- Python 3.11+
- Node.js 18+

Backend (FastAPI)

1. Create virtual environment and install deps

```powershell
cd dev-bot-trader-main
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Create a local `.env` from the example and set required keys

```powershell
cp .env.example .env
# edit .env and fill BYBIT_API_KEY, BYBIT_API_SECRET, GROQ_API_KEY, TELEGRAM_BOT_TOKEN
```

3. Run the API

```powershell
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend (Vite + React)

```powershell
cd ..\devbot-trader-dashboard
npm install
npm run dev
```

Open `http://localhost:5173` (Vite) and API at `http://127.0.0.1:8000`.
