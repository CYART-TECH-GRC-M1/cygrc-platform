<<<<<<< HEAD
deployment configuration files
=======
# Deployment Configuration

## Backend

Run the API with production Keycloak authentication enabled:

```bash
KEYCLOAK_ENABLED=true LOCAL_AUTH_ENABLED=false uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Configure the variables in the repository `.env.example` through the deployment secret manager. Never enable `LOCAL_AUTH_ENABLED` in production.

Required Keycloak values:

- Realm: `KEYCLOAK_REALM_NAME`
- Confidential or public client: `KEYCLOAK_CLIENT_ID`
- Audience mapper: add `KEYCLOAK_AUDIENCE` to the access token `aud` claim
- Roles: assign realm roles or client roles under the configured client

The API validates the token signature against the realm JWKS endpoint, issuer, audience, expiration, and issued roles. All non-auth API routers require a valid bearer token.

## Frontend

Build and run the root Next.js application:

```bash
npm ci
npm run build
npm run start
```

Set `BACKEND_API_URL` to the deployed API base ending in `/api/v1`. The browser uses same-origin Next routes for login and profile requests, so backend credentials stay server-side and CORS should allow only the deployed frontend origin through `CORS_ORIGINS`.

## Smoke checks

```bash
curl -f http://localhost:8000/health
curl -i http://localhost:8000/api/v1/auth/me
curl -I http://localhost:3000/login
```

Expected results are `200`, `401`, and `200` respectively. A real Keycloak login should return a token whose `iss` matches the configured realm URL and whose `aud` contains `KEYCLOAK_AUDIENCE`.
>>>>>>> origin/Abhishek
