# Tenant Auto-Provisioning & Framework Seeding — API

Module API for the backend work in:

- `backend/services/provisioning.py`
- `database/seeders/framework_seeder.py`
- `backend/models/tenant_control.py`
- `POST /api/v1/tenants/` (background trigger)
- `POST /api/v1/tenants/{tenant_id}/provision`
- `GET /api/v1/tenants/{tenant_id}/controls`

Full platform curl guide (auth, users, catalog CRUD): [api.md](./api.md)

---

## Base URL

This machine already uses **port 8000 for Splunk**. CyGRC uvicorn is:

**`http://localhost:8080`**

Swagger: [http://localhost:8080/docs](http://localhost:8080/docs)

On Windows PowerShell use `curl.exe` (plain `curl` is an alias for `Invoke-WebRequest`).

---

## What this module does

When a tenant is registered:

1. HTTP **201** is returned immediately.
2. A FastAPI **BackgroundTasks** job opens its **own** DB session (never the closed request session).
3. It seeds the **shared catalog** if missing: **ISO 27001** version **2022**, **SOC 2** version **2017**.
4. It inserts **tenant_controls** mappings for baseline controls (Access Control + Security Policies).
5. Catalog `Framework` / `Control` rows are **not** tenant-scoped. Tenants are linked only via `tenant_controls` (`tenant_id` + `control_id`, unique composite index).

If background seeding races or fails, call **retry provision** then **list mapped controls**. Tenant create still succeeds even if provisioning fails (logged only).

---

## Endpoints in this module

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| `POST` | `/api/v1/tenants/` | none | Create tenant; enqueue provision |
| `POST` | `/api/v1/tenants/{tenant_id}/provision` | none | Sync retry seed (idempotent) |
| `GET` | `/api/v1/tenants/{tenant_id}/controls` | none | List this tenant’s mapped controls |
| `GET` | `/api/v1/frameworks/` | none | Shared catalog (expect ISO 27001, SOC 2 after provision) |
| `GET` | `/api/v1/controls/?framework_id=` | none | Shared catalog controls for one framework |

Related (not owned by this module, used in the same flow):

| Method | Path | Notes |
| --- | --- | --- |
| `GET` | `/health` | Confirm API is up |
| `POST` | `/api/v1/auth/login` | Optional; JWT is not required for the routes above |
| `GET` | `/api/v1/tenants/{tenant_id}` | Tenant profile |

---

## 1. Health

**GET** `/health`

Confirm the API process is running.

```powershell
curl.exe -s http://localhost:8080/health
```

**200**

```json
{"status": "Healthy"}
```

---

## 2. Create tenant (triggers background provision)

**POST** `/api/v1/tenants/`

- Headers: `Content-Type: application/json`
- Body: `name` (required), `domain` (optional, unique), `subscription_plan` (optional, default `FREE`)

```powershell
curl.exe -s -X POST http://localhost:8080/api/v1/tenants/ -H "Content-Type: application/json" -d "{\"name\":\"Acme Corp\",\"domain\":\"acme.example\",\"subscription_plan\":\"FREE\"}"
```

**201**

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

Copy `tenant_id` → `TENANT_ID`.

**Errors**

| Code | When |
| --- | --- |
| 400 | `domain` already exists |
| 422 | Missing `name` or invalid JSON |

Provisioning is **async**. Do not assume mappings exist in the same millisecond as 201. Call section 3, then section 4.

---

## 3. Retry provision (NEW)

**POST** `/api/v1/tenants/{tenant_id}/provision`

Synchronous, **idempotent**. Ensures catalog frameworks exist, then inserts missing `(tenant_id, control_id)` rows.

- Headers: none required
- Body: none

```powershell
curl.exe -s -X POST http://localhost:8080/api/v1/tenants/TENANT_ID/provision
```

**200** (first run)

```json
{
  "tenant_id": "TENANT_ID",
  "frameworks_seeded": ["ISO 27001", "SOC 2"],
  "mappings_created": 9,
  "mappings_skipped": 0
}
```

**200** (second run — no duplicates)

```json
{
  "tenant_id": "TENANT_ID",
  "frameworks_seeded": ["ISO 27001", "SOC 2"],
  "mappings_created": 0,
  "mappings_skipped": 9
}
```

**Errors**

| Code | When |
| --- | --- |
| 404 | Tenant not found |
| 422 | `tenant_id` is not a UUID |

---

## 4. List tenant mapped controls (NEW)

**GET** `/api/v1/tenants/{tenant_id}/controls`

Join `tenant_controls` + catalog `controls` + `frameworks`. Expect **Access Control** and **Security Policies** in `control_name` / descriptions.

```powershell
curl.exe -s http://localhost:8080/api/v1/tenants/TENANT_ID/controls
```

**200** (array; one row shown)

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

**Errors**

| Code | When |
| --- | --- |
| 404 | Tenant not found |
| 422 | Invalid UUID |

---

## 5. Catalog frameworks (after seed)

**GET** `/api/v1/frameworks/`

Shared catalog (not per-tenant). After provision you should see **ISO 27001** / `2022` and **SOC 2** / `2017`.

```powershell
curl.exe -s http://localhost:8080/api/v1/frameworks/
```

**200**

```json
[
  {
    "framework_id": "FRAMEWORK_ID",
    "framework_name": "ISO 27001",
    "version": "2022",
    "description": "ISO/IEC 27001:2022 information security management baseline catalog.",
    "created_at": "2026-08-30T10:00:00"
  },
  {
    "framework_id": "FRAMEWORK_ID_SOC",
    "framework_name": "SOC 2",
    "version": "2017",
    "description": "SOC 2 Trust Services Criteria (2017) baseline catalog.",
    "created_at": "2026-08-30T10:00:00"
  }
]
```

Copy ISO `framework_id` → `FRAMEWORK_ID`.

One framework:

```powershell
curl.exe -s http://localhost:8080/api/v1/frameworks/FRAMEWORK_ID
```

**404** if id does not exist.

---

## 6. Catalog controls by framework

**GET** `/api/v1/controls/?framework_id=FRAMEWORK_ID`

Controls are global. Tenant assignment is only via section 4.

```powershell
curl.exe -s "http://localhost:8080/api/v1/controls/?framework_id=FRAMEWORK_ID"
```

**200** — ISO baseline includes `A.5.1`, `A.5.2`, `A.8.2`, `A.8.3`, `A.8.5`. SOC includes `CC1.1`, `CC6.1`, `CC6.2`, `CC6.3`.

---

## Happy path (this module)

```powershell
# 1. Health
curl.exe -s http://localhost:8080/health

# 2. Create tenant — copy tenant_id from JSON
curl.exe -s -X POST http://localhost:8080/api/v1/tenants/ -H "Content-Type: application/json" -d "{\"name\":\"Acme Corp\",\"domain\":\"acme.example\",\"subscription_plan\":\"FREE\"}"

# 3. Retry provision (wait is not required if you call this)
curl.exe -s -X POST http://localhost:8080/api/v1/tenants/TENANT_ID/provision

# 4. Mapped controls — Access Control + Security Policies
curl.exe -s http://localhost:8080/api/v1/tenants/TENANT_ID/controls

# 5. Catalog frameworks — ISO 27001 and SOC 2
curl.exe -s http://localhost:8080/api/v1/frameworks/

# 6. Catalog controls for ISO (replace FRAMEWORK_ID)
curl.exe -s "http://localhost:8080/api/v1/controls/?framework_id=FRAMEWORK_ID"
```

Git Bash helper (unique domain so 400 does not fire):

```bash
BASE=http://localhost:8080

TENANT_ID=$(curl.exe -s -X POST $BASE/api/v1/tenants/ \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Acme Corp\",\"domain\":\"acme-$(date +%s).example\",\"subscription_plan\":\"FREE\"}" \
  | python -c "import sys,json; print(json.load(sys.stdin)['tenant_id'])")

curl.exe -s -X POST $BASE/api/v1/tenants/$TENANT_ID/provision
curl.exe -s $BASE/api/v1/tenants/$TENANT_ID/controls
curl.exe -s $BASE/api/v1/frameworks/
```

---

## Baseline catalog this seeder maps

**ISO 27001:2022**

| Code | Name (contains) |
| --- | --- |
| A.5.1 | Security Policies |
| A.5.2 | Roles and responsibilities |
| A.8.2 | Access Control (privileged access) |
| A.8.3 | Access Control (restriction) |
| A.8.5 | Access Control (authentication) |

**SOC 2:2017**

| Code | Name (contains) |
| --- | --- |
| CC1.1 | security policies |
| CC6.1 | Access Control |
| CC6.2 | Credentials / authentication |
| CC6.3 | Least privilege / Access Control |

Descriptions are short original summaries (not copyrighted standard text).

---

## Data model (for reviewers)

```
frameworks          (global catalog)
    └── controls    (global catalog; NO tenant_id)

tenants
    └── tenant_controls
            mapping_id UUID PK
            tenant_id  FK tenants ON DELETE CASCADE
            control_id FK controls ON DELETE CASCADE
            status, seeded_at
            UNIQUE (tenant_id, control_id)
            INDEX ix_tenant_controls_tenant_id_control_id (tenant_id, control_id) UNIQUE
```
