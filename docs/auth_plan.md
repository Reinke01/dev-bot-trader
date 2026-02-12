# Auth Plan (JWT) - proposta de implementação

Resumo
- Autenticação: JWT (access + refresh)
- Tokens: access curto (ex: 15m), refresh longo (ex: 7d)
- Armazenamento de refresh tokens: DB ou Redis para permitir revogação
- Roles: admin, user, viewer

Endpoints propostos
- POST /auth/login -> retorna { access_token, refresh_token }
- POST /auth/refresh -> aceita refresh token, retorna novo access token
- POST /auth/logout -> revoga refresh token

Recomendações
- Use python-jose ou PyJWT; armazene JWT_SECRET em secret manager
- Use HTTPS em produção; proteja refresh tokens via httpOnly cookies
# Auth Plan (JWT) - proposta de implementação

Resumo
- Autenticação: JWT (access + refresh)
- Tokens: `access` curto (ex: 15m), `refresh` mais longo (ex: 7d)
- Armazenamento de refresh tokens: servidor (DB) ou store (Redis) para permitir revogação
- Roles: `admin`, `user`, `viewer` (pode mapear permissões por endpoint)
- Rate limiting: por IP e por usuário (ex.: 10 req/s por user para endpoints sensíveis)
- Audit log: registrar eventos de login, token refresh, falha de autenticação, logout

Endpoints propostos
- POST `/auth/login` -> retorna `{ access_token, refresh_token, token_type }`
- POST `/auth/refresh` -> aceita refresh token, retorna novo access token
- POST `/auth/logout` -> revoga refresh token

Estrutura simplificada
- Gerar chave `JWT_SECRET` (não comitar) e definir `JWT_ALGORITHM` (ex: HS256)
- Middleware que valida `Authorization: Bearer <token>` e injeta `current_user` no contexto
- Decorator/Depends para verificar roles por rota

Recomendações
- Use `python-jose` ou `PyJWT` para tokens; armazene `JWT_SECRET` em secret manager
- Use HTTPS em produção; não confiar em envs locais para produção sem vault
- Implementar política de refresh token rotation para maior segurança

Audit & Rate Limiting
- Registre em DB (tabela `auth_audit`) eventos: user_id, ip, user_agent, event_type (login, refresh, fail), timestamp
- Configure rate limit com `slowapi` (Starlette/ FastAPI) ou NGINX
