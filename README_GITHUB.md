# Dev Bot Trader

O Dev Bot Trader é um projeto avançado de trading algorítmico para criptomoedas. Combina estratégias quantitativas, backtesting com VectorBT, otimização de parâmetros e integração com corretoras (ex: Bybit). O objetivo é oferecer uma base para desenvolvimento de estratégias, execução em live trading e automação com observabilidade e segurança.

**Sumário rápido**
- **Backend:** FastAPI (Python) — código em `dev-bot-trader-main/src`
- **Frontend:** Vite + React — código em `devbot-trader-dashboard`
- **Scripts:** `scripts/run_backend.ps1`, `scripts/run_front.ps1` para desenvolvimento no Windows
- **Docs:** `docs/` com guias de deploy, segurança e operação

## Começando

Você pode fazer fork e clonar este repositório. Para clonar:

```bash
git clone <URL_DO_SEU_FORK>
cd dev-bot-trader
```

### Requisitos
- Python 3.11+ (recomendo instalar e marcar "Add Python to PATH")
- Git
- Node.js 18+ (para o dashboard)

## Rodando localmente (Windows — PowerShell)

1) Backend: cria/usa `.venv`, instala dependências e inicia a API.

```powershell
# na raiz do repositório
.\scripts\run_backend.ps1
```

2) Frontend: instala dependências do Node (se necessário) e inicia o Vite.

```powershell
cd devbot-trader-dashboard
.\scripts\run_front.ps1
```

Endpoints úteis (após o backend rodando):
- `http://127.0.0.1:8000/health` — healthcheck
- `http://127.0.0.1:8000/docs` — documentação OpenAPI
- `http://localhost:8080` — frontend (Vite)

## Variáveis de ambiente

Nunca committe chaves ou `.env` no repositório. Há exemplos de variáveis em:

- `dev-bot-trader-main/.env.example` (backend)
- `devbot-trader-dashboard/.env.example` (frontend)

Preencha suas chaves da Bybit e Telegram conforme o `*.env.example` antes de rodar em produção.

## Rodando no Render (ou outro PaaS)

- Crie um background worker ou web service e aponte o comando de start para o script de live trading (ex: `python src/live_trading/double_ema_breakout_orders.py`).
- Configure `BYBIT_API_KEY` e `BYBIT_API_SECRET` nas environment variables da sua aplicação.

## Funcionalidades planejadas (resumo)

- Logs de execução (pensamentos, ações e trades)
- Notificações (Telegram, Discord)
- Registro de trades e resultados (SQLite / MongoDB)
- Integração com múltiplas corretoras (Bybit, Binance, ccxt)
- Otimização de estratégias (GridSearch, DEAP, neuroevolution)
- Backtesting com VectorBT e execução paralela de jobs
- UI para configuração e monitoramento (React + dashboard)

## TODO (principais pontos)

- Adicionar sistema de logs e persistência de trades
- Refatorar código para usar inglês em variáveis/funções críticas
- Adicionar cobertura de testes
- Melhorar a coleta e preparação de dados (separar fetch/indicators)
- Opcional: containers Docker para backend e frontend

## Contribuindo

1) Abra uma issue descrevendo a proposta.
2) Faça um fork, crie uma branch e um PR com uma descrição clara.
3) Não inclua chaves nem arquivos `.env` em commits.

## Licença

Este repositório usa licença MIT por padrão (ou ajuste conforme necessário).

---

Se quiser, eu posso:

- Subir este conteúdo para `README.md` no root (substituindo o arquivo atual).
- Criar versões em `README.pt-BR.md` e `README.en.md`.
- Gerar um texto curto para a descrição do repositório no GitHub.

Diga qual formato prefere e eu aplico as mudanças finais.
