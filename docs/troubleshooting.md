# Troubleshooting

Common problems and fixes for local development.

1) ModuleNotFoundError: No module named 'src'

- Causa: você executou `python -m uvicorn src.main:app` a partir da raiz do repositório mas o código da API está em `dev-bot-trader-main/src` (ou outra pasta). O Python não encontra `src` no path.
- Solução rápida: use o script de execução que ajusta `--app-dir` automaticamente:

  ```powershell
  .\scripts\run_backend.ps1
  ```

- Solução manual: rode de dentro da pasta que contém `src`:

  ```powershell
  cd dev-bot-trader-main
  python -m uvicorn api.main:app --reload --app-dir src
  ```

2) requirements.txt não encontrado / dependências ausentes

- Causa: alguns scripts esperam `requirements.txt` dentro da pasta usada como backend.
- Solução: use `scripts/run_backend.ps1` que instalará as dependências a partir de `dev-bot-trader-main/requirements.txt` ou `backend/requirements.txt` se presentes.

3) Secrets foram acidentalmente versionados

- Verifique `.gitignore` (já cobre `.env` e `.venv`). Se você encontrar chaves em commits antigos, siga o guia em `docs/SECURITY.md` para remover usando `git filter-repo` ou `git filter-branch` e rotacione as chaves.

4) Erros comuns de Windows PowerShell

- Se scripts PowerShell não rodarem, execute no PowerShell com permissões adequadas e libere a execução de scripts temporariamente:

  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\scripts\run_backend.ps1
  ```
