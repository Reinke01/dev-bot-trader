Rodando localmente (PowerShell - Windows)

Pré-requisitos:
- Python 3.11+
- Node 18+
- Git

Passos resumidos:
1) Na raiz do repositório (ex: E:\Projetos\dev-bot-trader), rode:
   .\scripts\run_backend.ps1

2) Em outra janela PowerShell, rode:
   .\scripts\run_front.ps1

Validações rápidas:
- GET http://127.0.0.1:8000/health
- Abrir http://127.0.0.1:8000/docs
- Abrir http://localhost:8080

Se algo falhar:
- Remova `.venv` antigo e recrie o venv no backend.
- Rode `npm install` manualmente na pasta do frontend se dependências faltarem.
