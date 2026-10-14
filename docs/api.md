# CyGRC Platform API (backend)

**Provisioning module (tenant seed + mapped controls):** [provisioning-api.md](./provisioning-api.md)

On this machine Splunk uses port 8000. CyGRC is typically:

Base URL: `http://localhost:8080`

Interactive OpenAPI/Swagger UI: [http://localhost:8080/docs](http://localhost:8080/docs)  
OpenAPI JSON: [http://localhost:8080/api/v1/openapi.json](http://localhost:8080/api/v1/openapi.json)

If you started uvicorn on 8000 instead, replace `8080` with `8000` in every curl below.

This guide is meant to be run with **curl only** (no frontend). Copy IDs from JSON responses into later commands: `TENANT_ID`, `TOKEN`, `FRAMEWORK_ID`, `CONTROL_ID`, `USER_ID`.

---

## Start the backend

From the `cygrc-platform` root (the folder that contains `backend/` and `requirements.txt`):

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows Git Bash / Linux / macOS:
# source .venv/Scripts/activate   # Git Bash on Windows
# source .venv/bin/activate       # Linux / macOS

pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8080
```

Apply the mapping-table migration (once per database):

```bash
alembic -c backend/alembic.ini upgrade head
```

Configure PostgreSQL via `backend/.env` or environment variables (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, etc.). The API uses SQLAlchemy async (`postgresql+asyncpg`).

### curl on Windows

PowerShell aliases `curl` to `Invoke-WebRequest`. Use **`curl.exe`** so these examples work:

```powershell
curl.exe -s http://localhost:8000/health
```

Git Bash can use `curl` as in the examples below. JSON bodies use escaped double quotes so the same one-liners work in **cmd** and **PowerShell** with `curl.exe`. Multi-line `\` continuations work in Git Bash / Linux / macOS.

---

## Auth notes

Login is **temporary and hardcoded** (not the `users` table):

| Email | Password | Role |
| --- | --- | --- |
| `admin@test.com` | `adminpass123` | Admin |
| `employee@test.com` | `employeepass123` | Employee |

JWTs include `sub` (user id), `tenant_id`, and `role`.

Routes that call `get_current_tenant_id` accept **either**:

1. `Authorization: Bearer TOKEN` (tenant taken from the JWT), or  
2. `X-Tenant-ID: TENANT_ID` (dev/testing fallback)

If neither is valid, those routes return **401**.

Provisioning after `POST /api/v1/tenants/` runs in a **FastAPI BackgroundTasks** job with its **own** database session. The create response returns **201 immediately**. Wait a second, or call `POST /api/v1/tenants/{tenant_id}/provision`, then `GET /api/v1/tenants/{tenant_id}/controls`.

---

## Health

### GET `/health`

Liveness check.

- Headers: none  
- Body: none  

```bash
curl.exe -s http://localhost:8000/health
```

Success:

```json
{"status": "Healthy"}
```

### GET `/`

Welcome payload and docs hint.

```bash
curl.exe -s http://localhost:8000/
```

Success:

```json
{"message": "Welcome to CyGRC Platform API 🚀", "docs": "/docs"}
```

---

## Auth

### POST `/api/v1/auth/login`

Issue a JWT for the temporary test users.

- Headers: `Content-Type: application/json`  
- Body: `email`, `password`  

```bash
curl.exe -s -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"email\":\"admin@test.com\",\"password\":\"adminpass123\"}"
```

Success (`200`):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Save the token (Git Bash):

```bash
TOKEN=$(curl.exe -s -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"email\":\"admin@test.com\",\"password\":\"adminpass123\"}" | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

PowerShell:

```powershell
$login = curl.exe -s -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"email\":\"admin@test.com\",\"password\":\"adminpass123\"}" | ConvertFrom-Json
$TOKEN = $login.access_token
```

Errors:

- **401** — unknown email or wrong password (`Incorrect email or password.`)  
- **422** — invalid JSON / missing fields / invalid email format  

---

## Tenants

### POST `/api/v1/tenants/`

Register a tenant. After commit, background provisioning seeds catalog frameworks **ISO 27001** (version **2022**) and **SOC 2** (version **2017**) and maps baseline controls (Access Control, Security Policies) onto the tenant.

- Headers: `Content-Type: application/json`  
- Auth: not required  
- Body: `name` (required), `domain` (optional, unique), `subscription_plan` (optional, default `FREE`)  

```bash
curl.exe -s -X POST http://localhost:8000/api/v1/tenants/ -H "Content-Type: application/json" -d "{\"name\":\"Acme Corp\",\"domain\":\"acme.example\",\"subscription_plan\":\"FREE\"}"
```

Success (`201`):

```json
{
  "name": "Acme Corp",
  "domain": "acme.example",
  "subscription_plan": "FREE",
  "status": "ACTIVE",
  "tenant_id": "TENANT_ID",
  "created_at": "2026-08-30T10:00:00",
  "updated_at": "2026-08-30T10:00:00"
}
```

Copy `tenant_id` → `TENANT_ID`. Provisioning is async: wait briefly or call the retry endpoint below. Create still returns **201** if background seeding fails (check server logs).

Errors:

- **400** — `domain` already exists  
- **422** — validation error (e.g. missing `name`)  

### GET `/api/v1/tenants/`

List tenants (`skip`, `limit` query params).

- Headers: none  

```bash
curl.exe -s "http://localhost:8000/api/v1/tenants/?skip=0&limit=100"
```

Success (`200`): JSON array of tenant objects (same shape as create).

### GET `/api/v1/tenants/me`

Current tenant from JWT `tenant_id` or `X-Tenant-ID`.

- Headers: `Authorization: Bearer TOKEN` **and/or** `X-Tenant-ID: TENANT_ID`  

```bash
curl.exe -s http://localhost:8000/api/v1/tenants/me -H "Authorization: Bearer TOKEN"
```

```bash
curl.exe -s http://localhost:8000/api/v1/tenants/me -H "X-Tenant-ID: TENANT_ID"
```

Success (`200`): one tenant object.

Errors:

- **401** — missing/invalid token and no `X-Tenant-ID`  
- **400** — tenant id is not a UUID  
- **404** — tenant not in database (hardcoded login uses `00000000-0000-0000-0000-00000000000a`, which may **404** unless that row exists — use `X-Tenant-ID` with a tenant you created)  

### GET `/api/v1/tenants/{tenant_id}`

Fetch one tenant by id.

```bash
curl.exe -s http://localhost:8000/api/v1/tenants/TENANT_ID
```

Success (`200`): tenant object.

Errors:

- **404** — tenant not found  
- **422** — `tenant_id` is not a UUID  

### PUT `/api/v1/tenants/{tenant_id}`

Partial update.

- Headers: `Content-Type: application/json`  
- Body: any of `name`, `domain`, `subscription_plan`, `status` (`ACTIVE` | `INACTIVE` | `SUSPENDED`)  

```bash
curl.exe -s -X PUT http://localhost:8000/api/v1/tenants/TENANT_ID -H "Content-Type: application/json" -d "{\"subscription_plan\":\"BASIC\"}"
```

Success (`200`): updated tenant object.

Errors:

- **404** — tenant not found  
- **400** / **422** — invalid body (e.g. duplicate domain depending on DB constraints)  

### POST `/api/v1/tenants/{tenant_id}/provision` (retry seed)

Synchronously seed the **shared** catalog if missing and insert baseline `tenant_controls` mappings. **Idempotent**: a second call skips existing `(tenant_id, control_id)` pairs.

- Headers: none required  
- Body: none  

```bash
curl.exe -s -X POST http://localhost:8000/api/v1/tenants/TENANT_ID/provision
```

Success (`200`):

```json
{
  "tenant_id": "TENANT_ID",
  "frameworks_seeded": ["ISO 27001", "SOC 2"],
  "mappings_created": 9,
  "mappings_skipped": 0
}
```

Second run typically has `"mappings_created": 0` and `"mappings_skipped": 9`.

Errors:

- **404** — tenant not found  
- **422** — invalid UUID  

### GET `/api/v1/tenants/{tenant_id}/controls`

List this tenant’s mapped catalog controls (join mapping + control + framework). Use this to confirm Access Control and Security Policies baselines.

```bash
curl.exe -s http://localhost:8000/api/v1/tenants/TENANT_ID/controls
```

Success (`200`):

```json
[
  {
    "mapping_id": "MAPPING_ID",
    "tenant_id": "TENANT_ID",
    "control_id": "CONTROL_ID",
    "mapping_status": "ACTIVE",
    "seeded_at": "2026-08-30T10:00:01",
    "control_code": "A.5.1",
    "control_name": "Policies for information security (Security Policies)",
    "description": "Define and maintain information security policies approved by leadership.",
    "control_status": "ACTIVE",
    "framework_id": "FRAMEWORK_ID",
    "framework_name": "ISO 27001",
    "framework_version": "2022"
  }
]
```

Errors:

- **404** — tenant not found  

---

## Users

### POST `/api/v1/users/`

Create a user under a tenant.

- Headers: `Content-Type: application/json`  
- Optional: `Authorization: Bearer TOKEN` or `X-Tenant-ID: TENANT_ID` if `tenant_id` is omitted from the body  
- Body: `first_name` (required), `email` (required), `last_name`, `keycloak_id`, `tenant_id`  

```bash
curl.exe -s -X POST http://localhost:8000/api/v1/users/ -H "Content-Type: application/json" -d "{\"tenant_id\":\"TENANT_ID\",\"first_name\":\"Ada\",\"last_name\":\"Lovelace\",\"email\":\"ada@acme.example\"}"
```

Using header instead of body `tenant_id`:

```bash
curl.exe -s -X POST http://localhost:8000/api/v1/users/ -H "Content-Type: application/json" -H "X-Tenant-ID: TENANT_ID" -d "{\"first_name\":\"Ada\",\"last_name\":\"Lovelace\",\"email\":\"ada@acme.example\"}"
```

Success (`201`):

```json
{
  "first_name": "Ada",
  "last_name": "Lovelace",
  "email": "ada@acme.example",
  "keycloak_id": null,
  "status": "ACTIVE",
  "user_id": "USER_ID",
  "tenant_id": "TENANT_ID",
  "created_at": "2026-08-30T10:00:00",
  "updated_at": "2026-08-30T10:00:00"
}
```

Errors:

- **400** — no tenant (body or header), or email already exists  
- **401** — no tenant in body and no valid `Authorization` / `X-Tenant-ID`  
- **404** — `tenant_id` does not exist  
- **422** — invalid email / missing `first_name`  

### GET `/api/v1/users/`

List users for the **current tenant** (JWT or `X-Tenant-ID`). Query: `skip`, `limit`.

- Headers: `Authorization: Bearer TOKEN` **or** `X-Tenant-ID: TENANT_ID`  

```bash
curl.exe -s "http://localhost:8000/api/v1/users/?skip=0&limit=100" -H "X-Tenant-ID: TENANT_ID"
```

```bash
curl.exe -s "http://localhost:8000/api/v1/users/" -H "Authorization: Bearer TOKEN"
```

Success (`200`): array of user objects.

Errors:

- **401** — tenant identity missing  
- **400** — tenant id is not a UUID  

---

## Frameworks (shared catalog)

Frameworks are **not** tenant-scoped. Seeding creates **ISO 27001** / **2022** and **SOC 2** / **2017** if they are missing.

### GET `/api/v1/frameworks/`

```bash
curl.exe -s http://localhost:8000/api/v1/frameworks/
```

Success (`200`):

```json
[
  {
    "framework_id": "FRAMEWORK_ID",
    "framework_name": "ISO 27001",
    "version": "2022",
    "description": "ISO/IEC 27001:2022 information security management baseline catalog.",
    "created_at": "2026-08-30T10:00:00"
  }
]
```

Copy `framework_id` → `FRAMEWORK_ID`.

### GET `/api/v1/frameworks/{framework_id}`

```bash
curl.exe -s http://localhost:8000/api/v1/frameworks/FRAMEWORK_ID
```

Success (`200`): one framework object.

Errors:

- **404** — framework not found  
- **422** — invalid UUID  

---

## Controls (shared catalog)

Controls belong to a framework. They do **not** have `tenant_id`. Tenant assignment is `GET /api/v1/tenants/{tenant_id}/controls`.

### GET `/api/v1/controls/`

Optional filter: `framework_id`.

```bash
curl.exe -s http://localhost:8000/api/v1/controls/
```

```bash
curl.exe -s "http://localhost:8000/api/v1/controls/?framework_id=FRAMEWORK_ID"
```

Success (`200`): array of:

```json
{
  "control_id": "CONTROL_ID",
  "framework_id": "FRAMEWORK_ID",
  "control_code": "A.8.2",
  "control_name": "Privileged access rights (Access Control)",
  "description": "Restrict and review privileged access to systems and data.",
  "status": "ACTIVE",
  "created_at": "2026-08-30T10:00:00"
}
```

### POST `/api/v1/controls/`

Create a catalog control.

- Headers: `Content-Type: application/json`  
- Body: `framework_id`, `control_code`, `control_name`, optional `description`, `status` (default `ACTIVE`)  

```bash
curl.exe -s -X POST http://localhost:8000/api/v1/controls/ -H "Content-Type: application/json" -d "{\"framework_id\":\"FRAMEWORK_ID\",\"control_code\":\"A.9.9\",\"control_name\":\"Example extra control\",\"description\":\"Tenant-independent catalog row.\"}"
```

Success (`201`): control object.

Errors:

- **404** — framework does not exist  
- **422** — validation error  

### GET `/api/v1/controls/{control_id}`

```bash
curl.exe -s http://localhost:8000/api/v1/controls/CONTROL_ID
```

Success (`200`): control object.

Errors:

- **404** — control not found  

### PUT `/api/v1/controls/{control_id}`

Partial update: `control_code`, `control_name`, `description`, `status`.

```bash
curl.exe -s -X PUT http://localhost:8000/api/v1/controls/CONTROL_ID -H "Content-Type: application/json" -d "{\"status\":\"ACTIVE\"}"
```

Success (`200`): updated control.

Errors:

- **404** — control not found  
- **422** — validation error  

---

## Happy path (chain these in order)

1. Health  
2. Login → save `TOKEN`  
3. Create tenant → save `TENANT_ID` (background provision starts)  
4. Retry provision (optional but recommended so you do not race the background job)  
5. List frameworks — expect **ISO 27001** and **SOC 2**  
6. List tenant mapped controls — expect **Access Control** and **Security Policies** baseline rows  
7. List catalog controls filtered by `framework_id`  

```bash
# 1. Health
curl.exe -s http://localhost:8000/health

# 2. Login
curl.exe -s -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"email\":\"admin@test.com\",\"password\":\"adminpass123\"}"

# 3. Create tenant (triggers background provision)
curl.exe -s -X POST http://localhost:8000/api/v1/tenants/ -H "Content-Type: application/json" -d "{\"name\":\"Acme Corp\",\"domain\":\"acme.example\",\"subscription_plan\":\"FREE\"}"

# 4. Retry provision (replace TENANT_ID)
curl.exe -s -X POST http://localhost:8000/api/v1/tenants/TENANT_ID/provision

# 5. Catalog frameworks — expect ISO 27001 and SOC 2
curl.exe -s http://localhost:8000/api/v1/frameworks/

# 6. Tenant mapped controls — expect Access Control and Security Policies baseline
curl.exe -s http://localhost:8000/api/v1/tenants/TENANT_ID/controls

# 7. Catalog controls for one framework (replace FRAMEWORK_ID from step 5)
curl.exe -s "http://localhost:8000/api/v1/controls/?framework_id=FRAMEWORK_ID"
```

Git Bash helper after step 2–3 (requires `python` on PATH):

```bash
TOKEN=$(curl.exe -s -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"email\":\"admin@test.com\",\"password\":\"adminpass123\"}" | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

TENANT_ID=$(curl.exe -s -X POST http://localhost:8000/api/v1/tenants/ -H "Content-Type: application/json" -d "{\"name\":\"Acme Corp\",\"domain\":\"acme-$(date +%s).example\",\"subscription_plan\":\"FREE\"}" | python -c "import sys,json; print(json.load(sys.stdin)['tenant_id'])")

curl.exe -s -X POST http://localhost:8000/api/v1/tenants/$TENANT_ID/provision
curl.exe -s http://localhost:8000/api/v1/frameworks/
curl.exe -s http://localhost:8000/api/v1/tenants/$TENANT_ID/controls

FRAMEWORK_ID=$(curl.exe -s http://localhost:8000/api/v1/frameworks/ | python -c "import sys,json; data=json.load(sys.stdin); print(next(f['framework_id'] for f in data if f.get('framework_name')=='ISO 27001'))")
curl.exe -s "http://localhost:8000/api/v1/controls/?framework_id=$FRAMEWORK_ID"
```

---

## Baseline catalog (what provisioning maps)

ISO 27001:2022 — `A.5.1` (Security Policies), `A.5.2`, `A.8.2` / `A.8.3` / `A.8.5` (Access Control).  
SOC 2:2017 — `CC1.1` (security policies), `CC6.1` / `CC6.2` / `CC6.3` (access).

Mappings live in `tenant_controls` with a unique composite index on `(tenant_id, control_id)`.
