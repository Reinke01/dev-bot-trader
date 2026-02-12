# Rotacionar credenciais (Bybit, Telegram, Google)

Siga os passos abaixo para revogar e recriar chaves/credenciais após uma exposição.

## 1) Bybit (API Key)
1. Acesse https://www.bybit.com/profile/api-management
2. Localize a API Key exposta e clique em **Delete/Revoke**.
3. Crie uma nova API Key com permissões mínimas necessárias (leitura para backtests; trading apenas para produção).
4. Atualize o arquivo `.env` local com `BYBIT_API_KEY` e `BYBIT_API_SECRET` novos.
5. Se o bot rodar em servidor, atualize os secrets do CI/infra e reinicie os serviços.

## 2) Telegram (Bot Token)
1. Abra o BotFather no Telegram.
2. Use `/token` ou `/revoke` conforme necessário para recriar o token do bot.
3. Atualize `TELEGRAM_BOT_TOKEN` em `.env` e nos secrets do servidor.
4. Gere um novo `TELEGRAM_CHAT_ID` (se necessário) usando `scripts/test_telegram.py`.

## 3) Google API Key
1. Acesse Google Cloud Console -> APIs & Credentials.
2. Localize a chave exposta e clique em "Delete".
3. Crie uma nova API Key e restrinja por IP/HTTP referrers e APIs permitidas.
4. Atualize `.env` e os secrets do servidor com `GOOGLE_API_KEY`.

## 4) Passos pós-rotação
- Verifique que não existam credenciais nos commits:
  ```bash
  git grep -n "AIza\|TELEGRAM_BOT_TOKEN\|BYBIT_API_KEY" || true
  ```
- Se as credenciais já fizeram parte do histórico git, reescreva o histórico (use com cuidado):
  - Recomendo usar `git filter-repo` ou `bfg-repo-cleaner`.
- Atualize variáveis de ambiente no servidor/CI e reinicie serviços.

## 5) Boas práticas
- Use Secret Manager (AWS/GCP/Azure) ou GitHub Secrets para CI.
- Nunca comitar `.env` com valores reais; mantenha `.env.example` no repo.
- Habilite varredura automática (gitleaks) no CI.
