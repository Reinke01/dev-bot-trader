# Security & Secrets Handling

- Never commit real secrets or `.env` files to Git. Keep secrets in environment variables.
- Use `dev-bot-trader-main/.env.example` and `devbot-trader-dashboard/.env.example` as templates.
- If a secret was accidentally committed, rotate the secret immediately at the provider and purge it from git history.

Suggested purge workflow (after rotating keys):

1. Install `git-filter-repo` (Windows WSL or Git for Windows with Python):

```powershell
pip install git-filter-repo
```

2. Example command to remove a literal secret string from history:

```powershell
git filter-repo --invert-paths --paths-glob 'dev-bot-trader-main/.env'
# or remove a specific token pattern:
git filter-repo --replace-text <(printf "gsk_XXXXXXXX==>gsk_REDACTED\n")
```

Notes:
- Rewriting history requires force-pushing and coordination with collaborators. After rewriting you must `git push --force --all` and ask all collaborators to re-clone or reset local branches.
- Always revoke and rotate compromised keys immediately.
# Segurança

Regras básicas:

- Nunca commit .env, chaves, tokens ou arquivos de configuração com segredos.
- Use `backend/.env.example` e `dashboard/.env.example` como referência apenas.
- Gere e mantenha `.secrets.baseline` local ao usar `detect-secrets`.

Rotação de chaves:
- Use um secret manager (AWS Secrets Manager, HashiCorp Vault) em produção.
- Procedimento: criar nova chave, atualizar secrets no servidor, reiniciar serviço, revogar chave antiga.

Ferramentas CI:
- Gitleaks no GitHub Actions para cada PR/push.
- Pre-commit `detect-secrets` local para evitar commits acidentais.
