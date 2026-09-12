# Debug Session: No Parameter Named "..."

- **Session ID**: no-parameter-error
- **Status**: [OPEN]
- **Created**: 2026-09-02
- **Symptom**: User reports `#problem:No parameter named "...` error, appearing twice.
- **Expected**: All imports, route registration, and Depends() resolve cleanly with no signature/argument errors.

## Hypotheses

| # | Hypothesis | Falsifiable | Status |
|---|-----------|-------------|--------|
| H1 | A `Depends(require_role([...]))` call passes keyword arg mismatch: `require_role` factory signature vs usage — likely the caller passes non-existent keyword param to inner closure. | TBD
| H2 | `jose.jwt.decode() call with unknown param (e.g. audience=None passed but python-jose wants `audience` under a different name, or `options` dict key mismatch. | TBD
| H3 | FastAPI route handler receives unhashable/unknown query parameter on an unhashable or unknown param in a Depends closure captured-param forwarder. | TBD
| H4 | Pydantic BaseModel schema field name mismatch (e.g. schema defines a field) in a way that `@router.post(response_model=...) uses unknown param. | TBD
| H5 | `Settings/config property called as function (e.g. `settings.keycloak_jwks_url()` instead of property, or httpx client called with unknown argument. | TBD

## Files to check:
- backend/core/config.py (19 properties not called as functions
- backend/core/security.py jose.jwt.decode() kwargs
- backend/core/dependencies.py Depends and require_role factory
- backend/api/v1/auth.py router, Depends calls
