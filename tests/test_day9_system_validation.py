import sys
import time
sys.path.insert(0, '.')
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

HEADERS = {"X-Tenant-ID": "00000000-0000-0000-0000-00000000000a"}


def test_team_a_high_volume_ingestion_load_test():
    """Team A: High-volume alert ingestion load test on Wazuh queue to verify sub-5s latency."""
    print("\n--- Team A: High-Volume Alert Ingestion Load Test ---")
    start_time = time.time()
    burst_count = 50

    for i in range(burst_count):
        wazuh_event = {
            "rule": {
                "id": 1000 + i,
                "level": 9,
                "description": f"Load Test Event #{i} - Suspicious Outbound Connection"
            },
            "agent": {
                "id": f"agent-{i:03d}",
                "name": f"host-loadtest-{i}"
            },
            "full_log": f"Log payload content for event {i}"
        }
        resp = client.post("/api/v1/alerts/wazuh/webhook", json=wazuh_event, headers=HEADERS)
        assert resp.status_code == 201

    elapsed_time = time.time() - start_time
    avg_latency_ms = (elapsed_time / burst_count) * 1000

    print(f"Ingested {burst_count} alerts in {elapsed_time:.2f}s (Avg latency: {avg_latency_ms:.2f}ms per alert).")
    assert elapsed_time < 5.0, f"Load test failed! Total time {elapsed_time:.2f}s exceeded 5.0s threshold."
    assert avg_latency_ms < 500, f"Latency per alert {avg_latency_ms:.2f}ms exceeded 500ms target."


def test_team_b_jira_sync_and_priority_validation():
    """Team B: Verify Jira ticket sync and CVE priority calculations with test datasets."""
    print("\n--- Team B: Jira Ticket Sync & Priority Calculations Validation ---")

    # Edge-case prioritization checks
    test_cases = [
        {"cvss": 9.8, "kev": True, "crit": "CRITICAL", "control": True, "expected_min": 14.0},
        {"cvss": 5.0, "kev": False, "crit": "LOW", "control": False, "expected_min": 6.0},
    ]

    for tc in test_cases:
        resp = client.post("/api/v1/vapt/cve/prioritize", json={
            "cvss_score": tc["cvss"],
            "is_cisa_kev": tc["kev"],
            "asset_criticality": tc["crit"],
            "has_mitigating_control": tc["control"]
        })
        assert resp.status_code == 200
        score = resp.json()["priority_score"]
        assert score >= tc["expected_min"]

    # Verify Jira Push
    jira_resp = client.post("/api/v1/vapt/jira/push", json={
        "cve_id": "CVE-2026-VAL-001",
        "cvss_score": 9.8,
        "affected_product": "Payment Gateway Service",
        "summary": "High risk vulnerability validated in load test"
    })
    assert jira_resp.status_code == 201
    assert jira_resp.json()["jira_ticket"]["ticket_key"].startswith("CYGRC-")


def test_team_c_chain_of_custody_tamper_test():
    """Team C: Execute Chain of Custody tamper test: Verify SHA-256 hash verification blocks altered files."""
    print("\n--- Team C: Chain of Custody Cryptographic Tamper Test ---")

    # 1. Store authentic evidence record
    original_hash = "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0"
    init_resp = client.post("/api/v1/chain-of-custody", json={
        "evidence_id": "EVID-TAMPER-TEST-001",
        "item_description": "Forensic Hard Drive Copy",
        "custodian_name": "Custodian Original",
        "custodian_email": "original@cygrc.local",
        "action": "COLLECTED",
        "hash_sha256": original_hash
    }, headers=HEADERS)
    assert init_resp.status_code == 201

    # 2. Attempt transfer with ALTERED / TAMPERED hash
    tampered_hash = "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    transfer_payload = {
        "evidence_id": "EVID-TAMPER-TEST-001",
        "previous_custodian": "Custodian Original",
        "new_custodian_name": "Custodian Attacker",
        "new_custodian_email": "attacker@cygrc.local",
        "new_location": "Unauthorized Location",
        "verification_hash_sha256": tampered_hash,
        "custodian_signature": "FAKE-SIG",
        "transfer_reason": "Tamper Test"
    }

    tamper_resp = client.post("/api/v1/chain-of-custody/transfer", json=transfer_payload, headers=HEADERS)
    # MUST be blocked with HTTP 400 Bad Request due to hash mismatch
    assert tamper_resp.status_code == 400, "Tamper test failed! Server accepted tampered hash."
    assert "SHA-256 hash mismatch" in tamper_resp.json()["detail"]
    print("Tamper test PASSED: SHA-256 hash mismatch successfully blocked tampered transfer.")


def test_team_d_end_to_end_stix_taxii_m2_to_m1_evidence_feeding():
    """Team D: Run end-to-end test of STIX/TAXII threat intel enrichment and M2-to-M1 evidence feeding."""
    print("\n--- Team D: End-to-End STIX/TAXII & M2-to-M1 Evidence Feeding Test ---")

    # 1. TAXII 2.1 Ingestion
    taxii_resp = client.post("/api/v1/taxii2/collections/misp-opencti-feed/objects/", json={
        "type": "bundle",
        "id": "bundle--val-99",
        "objects": [
            {
                "id": "indicator--val-ip-001",
                "type": "indicator",
                "name": "Validation C2 IP",
                "pattern": "[ipv4-addr:value = '203.0.113.88']",
                "confidence": 99
            }
        ]
    }, headers=HEADERS)
    assert taxii_resp.status_code == 202

    # 2. Feed SIEM alert signal to Module 1 GRC Control Status Engine
    bridge_resp = client.post("/api/v1/alerts/feed-control-evidence", json={
        "alert_id": "alert-val-88",
        "title": "C2 Traffic to 203.0.113.88",
        "severity": "CRITICAL",
        "control_id": "A.5.1"
    }, headers=HEADERS)
    assert bridge_resp.status_code == 200
    assert bridge_resp.json()["control_signal"]["calculated_compliance_status"] == "NON_COMPLIANT"


if __name__ == "__main__":
    test_team_a_high_volume_ingestion_load_test()
    test_team_b_jira_sync_and_priority_validation()
    test_team_c_chain_of_custody_tamper_test()
    test_team_d_end_to_end_stix_taxii_m2_to_m1_evidence_feeding()
    print("\nAll Day 9 System Validation & Load Tests passed successfully!")
