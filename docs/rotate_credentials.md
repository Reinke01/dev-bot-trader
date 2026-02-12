# Rotate Credentials

Recomendações para rotação de credenciais:

- Nunca armazenar chaves no código ou em arquivos commitados.
- Use um secret manager (AWS SSM, AWS Secrets Manager, HashiCorp Vault) para armazenar chaves.
- Procedimento de rotação:
  1. Gerar nova chave no provedor (ex: Bybit) e colocar no secret manager.
  2. Atualizar `secrets/backend.env` no servidor com a nova chave.
  3. Reiniciar serviço (`docker-compose restart backend` ou `systemctl restart devbot-backend`).
  4. Verificar logs e métricas para erros de autenticação.

Checklist:
- Atualizar documentação interna com data e responsável pela rotação.
- Revogar chaves antigas após verificação.
