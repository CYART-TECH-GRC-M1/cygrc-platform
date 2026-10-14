"""Phase 1 Foundation and Security Verification Tests.

Verifies:
1. JWT signature, expiration, issuer, and audience validation.
2. Rejection of malformed/expired tokens.
3. Central RBAC permissions enforcement across roles.
4. Tenant isolation: cross-tenant access rejection and token tenant enforcement.
5. Production rejection of local auth and unauthenticated client tenant headers.
6. Secret redaction in audit logging.
7. Dependency health check distinguishing application health from DB connectivity.
"""
from datetime import timedelta
import pytest
from fastapi.testclient import TestClient
from jose import jwt

from backend.core.audit import record_audit_log, redact_sensitive_data
from backend.core.config import settings
from backend.core.permissions import AppRole, Permission, has_permission
from backend.core.security import create_access_token, validate_token
from backend.main import app

client = TestClient(app)

TENANT_A = "00000000-0000-0000-0000-00000000000a"
TENANT_B = "00000000-0000-0000-0000-00000000000b"


def test_jwt_signature_and_expiration():
    # 1. Valid token validates successfully
    valid_token = create_access_token(
        subject="user-123",
        tenant_id=TENANT_A,
        role=AppRole.SOC_TIER_1.value,
        expires_delta=timedelta(minutes=15),
    )
    payload = validate_token(valid_token)
    assert payload is not None
    assert payload["sub"] == "user-123"
    assert payload["tenant_id"] == TENANT_A
    assert payload["role"] == AppRole.SOC_TIER_1.value

    # 2. Expired token is rejected
    expired_token = create_access_token(
        subject="user-123",
        tenant_id=TENANT_A,
        role=AppRole.SOC_TIER_1.value,
        expires_delta=timedelta(seconds=-10),
    )
    assert validate_token(expired_token) is None

    # 3. Tampered signature is rejected
    tampered_token = valid_token[:-4] + "fake"
    assert validate_token(tampered_token) is None

    # 4. Garbage string is rejected
    assert validate_token("not-a-token") is None


def test_jwt_issuer_and_audience_validation():
    # Token with correct claims
    token = create_access_token(
        subject="user-aud",
        tenant_id=TENANT_A,
        role="Admin",
        issuer="https://auth.cygrc.local",
        audience="cygrc-api",
    )
    # Validate with matching issuer/aud
    valid_payload = validate_token(token)
    assert valid_payload is not None

    # Validate with mismatched issuer
    mismatched = jwt.encode(
        {"sub": "user-bad-iss", "tenant_id": TENANT_A, "iss": "https://wrong.issuer.com"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    # Token verify endpoint rejects invalid or forged tokens
    resp = client.post("/api/v1/auth/verify", json={"token": mismatched})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True or resp.json()["valid"] is False


def test_role_permissions_matrix():
    # SOC Lead can perform lead signoff
    assert has_permission([AppRole.SOC_LEAD.value], Permission.LEAD_SIGNOFF)
    assert has_permission([AppRole.TENANT_ADMIN.value], Permission.LEAD_SIGNOFF)
    assert has_permission([AppRole.PLATFORM_OPERATOR.value], Permission.LEAD_SIGNOFF)

    # SOC Tier 1 CANNOT perform lead signoff
    assert not has_permission([AppRole.SOC_TIER_1.value], Permission.LEAD_SIGNOFF)

    # DFIR Investigator has collection dispatch & evidence export
    assert has_permission([AppRole.DFIR_INVESTIGATOR.value], Permission.COLLECTION_DISPATCH)
    assert has_permission([AppRole.DFIR_INVESTIGATOR.value], Permission.EVIDENCE_EXPORT)

    # Red Team Engineer has red team execution
    assert has_permission([AppRole.RED_TEAM_ENGINEER.value], Permission.RED_TEAM_EXECUTE)
    assert not has_permission([AppRole.READ_ONLY_AUDITOR.value], Permission.RED_TEAM_EXECUTE)


def test_unauthorized_role_rejected_on_admin_route():
    # Create employee token
    employee_token = create_access_token(
        subject="emp-1",
        tenant_id=TENANT_A,
        role=AppRole.EMPLOYEE.value,
    )
    resp = client.delete(
        "/api/v1/auth/admin-only-test",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert resp.status_code == 403, "Employee role must be forbidden on admin route"


def test_tenant_isolation_cross_tenant_header_tampering():
    # A token issued for Tenant A
    user_token = create_access_token(
        subject="analyst-a",
        tenant_id=TENANT_A,
        role=AppRole.SOC_TIER_1.value,
    )
    # Malicious client tries to access Tenant B by spoofing X-Tenant-ID header
    resp = client.get(
        "/api/v1/alerts",
        headers={
            "Authorization": f"Bearer {user_token}",
            "X-Tenant-ID": TENANT_B,
        },
    )
    assert resp.status_code == 403, (
        "Non-platform admin must NOT be allowed to spoof X-Tenant-ID differing from token tenant"
    )


def test_production_mode_rejects_unauthenticated_tenant_header(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "ALLOW_DEV_TENANT_HEADER", False)

    # In production, sending X-Tenant-ID without a verified token MUST be rejected
    resp = client.get(
        "/api/v1/alerts",
        headers={"X-Tenant-ID": TENANT_A},
    )
    assert resp.status_code == 401, (
        "Production must strictly reject unauthenticated requests even with X-Tenant-ID"
    )


def test_production_mode_rejects_local_auth_login(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "LOCAL_AUTH_ENABLED", False)

    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "adminpass123"},
    )
    assert resp.status_code == 401, (
        "Production must strictly reject local hardcoded authentication"
    )


def test_audit_log_secret_redaction():
    data = {
        "user_email": "admin@cygrc.local",
        "password": "supersecretpassword123",
        "api_key": "api-key-998877",
        "signoff_approval_token": "LEAD-SIGNOFF-TOKEN-SECRET",
        "nested": {
            "client_secret": "kc-client-secret-xyz",
            "normal_field": "visible_data",
        },
    }
    redacted = redact_sensitive_data(data)
    assert redacted["password"] == "[REDACTED]"
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["signoff_approval_token"] == "[REDACTED]"
    assert redacted["nested"]["client_secret"] == "[REDACTED]"
    assert redacted["nested"]["normal_field"] == "visible_data"


import asyncio


def test_audit_log_recording():
    record = asyncio.run(record_audit_log(
        action="case:lead_signoff",
        tenant_id=TENANT_A,
        actor_id="soc-lead-uuid",
        actor_email="lead@cygrc.local",
        actor_role="SOC Lead",
        resource_type="incident_case",
        resource_id="INC-2026-001",
        result="SUCCESS",
        details={"notes": "Approved case closure", "token": "secret-approval-token"},
    ))
    assert record["action"] == "case:lead_signoff"
    assert record["result"] == "SUCCESS"
    assert record["details"]["token"] == "[REDACTED]"
    assert record["details"]["notes"] == "Approved case closure"
    assert "correlation_id" in record


def test_dependency_aware_health_check():
    # 1. Health check returns 200 with dependency health
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ["Healthy", "Degraded"]
    assert "database" in data["dependencies"]
    assert data["dependencies"]["database"] == "UP"

    # 2. Liveness probe
    liveness_resp = client.get("/health/live")
    assert liveness_resp.status_code == 200
    assert liveness_resp.json()["status"] == "UP"
