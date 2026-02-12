# Release checklist

- Atualizar `requirements.txt` e `package.json` com versões desejadas.
- Rodar testes unitários (se existirem).
- Atualizar `CHANGELOG.md` (se existir) com notas da release.
- Verificar `pre-commit` e `gitleaks` limpos.
- Atualizar imagens Docker (tag) e `docker-compose.yml` se necessário.
- Criar tag Git e abrir PR para revisão.
