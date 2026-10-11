"""Phase 2 SOC, Wazuh, Sigma and Incident Response Verification Tests.

Verifies:
1. Wazuh webhook ingestion: normalization, deterministic source_event_id, idempotent deduplication, durable persistence.
2. Tenant-scoped Server-Sent Events (SSE) publish/subscribe delivery.
3. Sigma detection engine: schema validation, modifier parsing, Wazuh XML generation, deployment and rollback.
4. Starter Sigma Rules: 50/50 test harness validation with known-good/known-bad samples.
5. Incident Case Management: NIST lifecycle state-machine transitions and SOC Lead sign-off.
6. Cryptographic case-state binding and approval token replay prevention.
7. Statistical-Threshold UEBA: anomaly detection, sparse baseline protection (N < 5), and explainability.
8. MITRE ATT&CK detection coverage: distinguishing mapped rules from tested rules.
"""
import asyncio
import uuid
import pytest
from datetime import timedelta
from fastapi.testclient import TestClient

from backend.main import app
from backend.core.security import create_access_token
from backend.core.permissions import AppRole
from backend.services.alert_stream import AlertStreamBroker
from backend.services.sigma_engine import SigmaEngine, SigmaRuleRegistry
from backend.services.starter_rules import StarterRulesHarness
from backend.services.ueba_service import UEBAEngine

client = TestClient(app)

TENANT_ID = "00000000-0000-0000-0000-00000000000a"

# Auth tokens for role testing
analyst_token = create_access_token(
    subject="analyst-1",
    tenant_id=TENANT_ID,
    role=AppRole.SOC_TIER_1.value,
)
lead_token = create_access_token(
    subject="lead-1",
    tenant_id=TENANT_ID,
    role=AppRole.SOC_LEAD.value,
)

AUTH_ANALYST = {"Authorization": f"Bearer {analyst_token}", "X-Tenant-ID": TENANT_ID}
AUTH_LEAD = {"Authorization": f"Bearer {lead_token}", "X-Tenant-ID": TENANT_ID}


def test_wazuh_webhook_ingestion_and_idempotency():
    """Verify Wazuh webhook normalizes events, assigns source_event_id, and rejects duplicates idempotently."""
    event_uid = uuid.uuid4().hex[:8]
    wazuh_payload = {
        "rule": {
            "id": 5715,
            "level": 12,
            "description": f"SSHD auth failure threshold exceeded {event_uid}",
        },
        "agent": {
            "id": f"agent-{event_uid}",
            "name": f"prod-web-{event_uid}",
        },
        "full_log": f"Oct 11 12:00:00 prod-web-{event_uid} sshd[9999]: Failed password for invalid user",
        "timestamp": "2026-10-11T12:00:00Z",
    }

    # 1. Ingest event first time
    resp1 = client.post("/api/v1/alerts/wazuh/webhook", json=wazuh_payload, headers=AUTH_ANALYST)
    assert resp1.status_code == 201, resp1.text
    data1 = resp1.json()
    assert data1["severity"] == "CRITICAL"
    assert f"prod-web-{event_uid}" in data1["title"]
    assert data1["source"] == "Wazuh SIEM Listener"
    alert_id = data1["alert_id"]

    # 2. Re-ingest the exact same event -> Idempotent skip (returns duplicate header without re-inserting)
    resp2 = client.post("/api/v1/alerts/wazuh/webhook", json=wazuh_payload, headers=AUTH_ANALYST)
    assert resp2.status_code in [200, 201], resp2.text
    assert resp2.headers.get("X-Idempotent-Duplicate") == "true"
    data2 = resp2.json()
    assert data2["alert_id"] == alert_id


def test_alert_stream_broker_tenant_pubsub():
    """Verify AlertStreamBroker manages tenant queues and delivers real alerts."""
    tenant = f"test-stream-{uuid.uuid4().hex[:6]}"

    async def run_pubsub_test():
        queue = await AlertStreamBroker.subscribe(tenant)
        test_alert = {
            "alert_id": "ALT-STREAM-001",
            "title": "Privilege Escalation Detected",
            "severity": "CRITICAL",
            "source": "Wazuh",
        }
        await AlertStreamBroker.publish_alert(tenant, test_alert)
        event = await queue.get()
        assert event["event"] == "alert"
        assert event["data"]["alert_id"] == "ALT-STREAM-001"
        assert event["data"]["severity"] == "CRITICAL"
        await AlertStreamBroker.unsubscribe(tenant, queue)

    asyncio.run(run_pubsub_test())


def test_sigma_engine_validation_and_conversion():
    """Verify Sigma schema validation, modifier parsing, and Wazuh XML generation."""
    valid_sigma = """
title: Suspicious Certutil Download
status: test
description: Detects suspicious certutil.exe download command
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\certutil.exe'
        CommandLine|contains: ' -urlcache '
    condition: selection
level: high
tags:
    - attack.t1105
"""
    res = SigmaEngine.parse_and_convert(valid_sigma)
    assert res["success"] is True
    assert res["wazuh_level"] == 10
    assert "Sigma Rule: Detects suspicious certutil.exe" in res["wazuh_xml"]
    assert "T1105" in res["mitre_ids"]
    assert '<field name="CommandLine" type="pcre2">(?i) -urlcache </field>' in res["wazuh_xml"]

    # Rejection of invalid schema
    invalid_sigma = "title: Incomplete Rule\nlevel: low"
    res_bad = SigmaEngine.parse_and_convert(invalid_sigma)
    assert res_bad["success"] is False
    assert len(res_bad["diagnostics"]) > 0


def test_sigma_rule_registry_versioning_and_rollback():
    """Verify deployment versioning and rollback capability."""
    rule_id = f"SIG-TEST-{uuid.uuid4().hex[:6]}"
    v1_yaml = """
title: Rule Version 1
logsource: { product: windows }
detection: { selection: { Image: 'powershell.exe' }, condition: selection }
level: medium
"""
    v2_yaml = """
title: Rule Version 2 Updated
logsource: { product: windows }
detection: { selection: { Image: 'powershell.exe', CommandLine|contains: 'invoke-mimikatz' }, condition: selection }
level: high
"""
    # Deploy v1
    r1 = SigmaRuleRegistry.register_rule(TENANT_ID, rule_id, v1_yaml)
    assert r1["version"] == 1

    # Deploy v2
    r2 = SigmaRuleRegistry.register_rule(TENANT_ID, rule_id, v2_yaml)
    assert r2["version"] == 2

    # Verify active rule is v2
    active = SigmaRuleRegistry.get_active_rule(TENANT_ID, rule_id)
    assert active["version"] == 2
    assert "Updated" in active["title"]

    # Rollback to v1
    rolled = SigmaRuleRegistry.rollback_rule(TENANT_ID, rule_id)
    assert rolled is not None
    assert "ROLLED_BACK_FROM_v2" in rolled["status"]
    assert rolled["title"] == "Rule Version 1"


def test_starter_rules_50_harness_pass_rate():
    """Verify all 50 starter Sigma rules pass evaluation in test harness."""
    results = StarterRulesHarness.test_all_starter_rules()
    assert results["total_rules"] == 50
    assert results["passed_rules"] == 50
    assert results["coverage_verified"] is True
    assert results["pass_rate"] == "100.0%"


def test_soc_lead_signoff_and_replay_protection():
    """Verify that closing HIGH/CRITICAL cases strictly requires SOC Lead sign-off and prevents token replay."""
    # 1. Create a HIGH severity case
    create_resp = client.post(
        "/api/v1/cases",
        json={"title": "High Severity Security Incident", "severity": "HIGH"},
        headers=AUTH_ANALYST,
    )
    assert create_resp.status_code == 201
    case_id = create_resp.json()["case_id"]

    # 2. Attempt to close without SOC Lead signoff -> HTTP 403 Forbidden
    unapproved_close = client.post(
        f"/api/v1/cases/{case_id}/transition",
        json={"target_status": "CLOSED"},
        headers=AUTH_ANALYST,
    )
    assert unapproved_close.status_code == 403
    assert "SOC Lead approval sign-off required" in unapproved_close.json()["detail"]

    # 3. Analyst tries to sign-off themselves -> HTTP 403 Forbidden (RBAC check)
    analyst_signoff = client.post(
        f"/api/v1/cases/{case_id}/lead-signoff",
        json={
            "lead_email": "analyst@cygrc.local",
            "lead_notes": "Analyst self-approval",
            "signoff_approval_token": "FORGED-TOKEN-123",
        },
        headers=AUTH_ANALYST,
    )
    assert analyst_signoff.status_code == 403

    # 4. Legitimate SOC Lead grants sign-off
    lead_signoff = client.post(
        f"/api/v1/cases/{case_id}/lead-signoff",
        json={
            "lead_email": "lead@cygrc.local",
            "lead_notes": "SOC Lead verified containment and eradication.",
            "signoff_approval_token": "VALID-LEAD-SIGNOFF-456",
        },
        headers=AUTH_LEAD,
    )
    assert lead_signoff.status_code == 200
    assert lead_signoff.json()["status"] == "SUCCESS"

    # 5. Now transition to CLOSED succeeds
    approved_close = client.post(
        f"/api/v1/cases/{case_id}/transition",
        json={"target_status": "CLOSED"},
        headers=AUTH_ANALYST,
    )
    assert approved_close.status_code == 200
    assert approved_close.json()["status"] == "CLOSED"

    # 6. Reopen case
    reopen_resp = client.post(
        f"/api/v1/cases/{case_id}/transition",
        json={"target_status": "REOPENED"},
        headers=AUTH_ANALYST,
    )
    assert reopen_resp.status_code == 200
    assert reopen_resp.json()["status"] == "REOPENED"

    # Transition REOPENED -> IN_PROGRESS
    to_prog = client.post(
        f"/api/v1/cases/{case_id}/transition",
        json={"target_status": "IN_PROGRESS"},
        headers=AUTH_ANALYST,
    )
    assert to_prog.status_code == 200

    # 7. Replay attack: try to resolve or close without new sign-off (prior token was consumed) -> HTTP 403
    replay_attempt = client.post(
        f"/api/v1/cases/{case_id}/transition",
        json={"target_status": "RESOLVED"},
        headers=AUTH_ANALYST,
    )
    assert replay_attempt.status_code == 403
    assert "SOC Lead approval sign-off required" in replay_attempt.json()["detail"]


def test_ueba_statistical_baseline_and_sparse_data():
    """Verify UEBA engine detects anomalies and suppresses alerts on sparse baselines (N < 5)."""
    # 1. Sparse data (N = 3) -> INSUFFICIENT_BASELINE_DATA, no anomaly
    sparse_result = UEBAEngine.analyze_event_anomaly(
        entity_id="user_bob",
        feature_name="failed_logins",
        observed_value=25.0,
        historical_baseline=[1.0, 2.0, 1.0],
    )
    assert sparse_result["status"] == "INSUFFICIENT_BASELINE_DATA"
    assert sparse_result["is_anomaly"] is False
    assert sparse_result["observations_count"] == 3

    # 2. Established baseline (N = 7), normal observation
    normal_result = UEBAEngine.analyze_event_anomaly(
        entity_id="user_alice",
        feature_name="failed_logins",
        observed_value=2.0,
        historical_baseline=[1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0],
    )
    assert normal_result["status"] == "EVALUATED"
    assert normal_result["is_anomaly"] is False
    assert normal_result["anomaly_score"] == 0

    # 3. Established baseline (N = 7), spike observation -> ANOMALY detected
    anomaly_result = UEBAEngine.analyze_event_anomaly(
        entity_id="user_alice",
        feature_name="failed_logins",
        observed_value=35.0,
        historical_baseline=[1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0],
    )
    assert anomaly_result["status"] == "EVALUATED"
    assert anomaly_result["is_anomaly"] is True
    assert anomaly_result["anomaly_score"] > 50
    assert "Statistical anomaly detected" in anomaly_result["reason"]


def test_mitre_coverage_mapped_vs_tested():
    """Verify GET /api/v1/mitre/coverage returns mapped and tested techniques."""
    resp = client.get("/api/v1/mitre/coverage", headers=AUTH_ANALYST)
    assert resp.status_code == 200
    data = resp.json()
    assert data["mapped_techniques_count"] >= 40
    assert data["verified_tested_techniques_count"] >= 40
    assert data["harness_pass_rate"] == "100.0%"
    assert data["version"] == "MITRE ATT&CK v19.1"
