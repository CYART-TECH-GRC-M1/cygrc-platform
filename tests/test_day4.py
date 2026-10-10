import sys
sys.path.insert(0, '.')
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

HEADERS = {"X-Tenant-ID": "00000000-0000-0000-0000-00000000000a"}


def test_team_a_cases_ui_flow():
    # Test creation and list of NIST incident cases
    payload = {
        "title": "Day 4 SOC Triage Case Test",
        "nist_phase": "DETECTION_ANALYSIS",
        "severity": "CRITICAL",
        "assigned_analyst": "Senior Incident Handler"
    }
    resp = client.post("/api/v1/cases", json=payload, headers=HEADERS)
    assert resp.status_code == 201, resp.text
    case_id = resp.json()["case_id"]

    resp = client.get("/api/v1/cases", headers=HEADERS)
    assert resp.status_code == 200
    assert any(c["case_id"] == case_id for c in resp.json())


def test_team_b_vulnerability_prioritization_formula():
    # 1. Test calculation: CVSS=7.5, KEV=True (+3.0), Crit=HIGH (+3.0), Control=False (0.0) -> 13.5
    calc_payload = {
        "cvss_score": 7.5,
        "is_cisa_kev": True,
        "asset_criticality": "HIGH",
        "has_mitigating_control": False
    }
    resp = client.post("/api/v1/vapt/cve/prioritize", json=calc_payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["priority_score"] == 13.5
    assert data["priority_level"] == "P2_HIGH"

    # 2. Test calculation with mitigating control credit: CVSS=9.8, KEV=True (+3.0), Crit=CRITICAL (+4.0), Control=True (-2.0) -> 14.8 (P1_URGENT)
    calc_payload_mitigated = {
        "cvss_score": 9.8,
        "is_cisa_kev": True,
        "asset_criticality": "CRITICAL",
        "has_mitigating_control": True
    }
    resp2 = client.post("/api/v1/vapt/cve/prioritize", json=calc_payload_mitigated)
    assert resp2.status_code == 200, resp2.text
    data2 = resp2.json()
    assert data2["priority_score"] == 14.8
    assert data2["priority_level"] == "P1_URGENT"


def test_team_c_atomic_red_team_execution():
    # Test single-technique Atomic Red Team test execution
    atomic_payload = {
        "technique_id": "T1059.001",
        "technique_name": "PowerShell Command Execution",
        "target_asset_id": "WIN-SRV-DEV-01",
        "executor": "powershell",
        "command": "powershell.exe -Command \"Get-Process\""
    }
    resp = client.post("/api/v1/redteam/atomic/execute", json=atomic_payload, headers=HEADERS)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["execution_id"].startswith("ART-")
    assert len(data["execution_hash"]) == 64

    # Check history
    hist_resp = client.get("/api/v1/redteam/atomic/history", headers=HEADERS)
    assert hist_resp.status_code == 200
    assert any(h["execution_id"] == data["execution_id"] for h in hist_resp.json())


def test_team_d_alert_threat_intel_enrichment():
    # 1. Store STIX 2.1 indicator matching IP 198.51.100.42
    stix_payload = {
        "type": "indicator",
        "name": "Cobalt Strike C2 IP Indicator",
        "pattern": "[ipv4-addr:value = '198.51.100.42']",
        "confidence": 95,
        "labels": ["c2", "cobalt-strike"]
    }
    stix_resp = client.post("/api/v1/stix/objects", json=stix_payload, headers=HEADERS)
    assert stix_resp.status_code == 201

    # 2. Ingest SOC alert referencing 198.51.100.42
    alert_payload = {
        "title": "Outbound Connection to 198.51.100.42",
        "source": "Wazuh",
        "severity": "MEDIUM",
        "description": "Suspicious outbound session to 198.51.100.42"
    }
    alert_resp = client.post("/api/v1/alerts", json=alert_payload, headers=HEADERS)
    assert alert_resp.status_code == 201
    alert_id = alert_resp.json()["alert_id"]

    # 3. Trigger automatic STIX 2.1 enrichment
    enrich_resp = client.post(f"/api/v1/alerts/{alert_id}/enrich", headers=HEADERS)
    assert enrich_resp.status_code == 200, enrich_resp.text
    enrich_data = enrich_resp.json()
    assert enrich_data["success"] is True
    assert enrich_data["enrichment"]["matched_indicators_count"] >= 1

    # Verify auto-escalated severity to CRITICAL
    alert_check = client.get(f"/api/v1/alerts/{alert_id}", headers=HEADERS)
    assert alert_check.json()["severity"] == "CRITICAL"


if __name__ == "__main__":
    test_team_a_cases_ui_flow()
    test_team_b_vulnerability_prioritization_formula()
    test_team_c_atomic_red_team_execution()
    test_team_d_alert_threat_intel_enrichment()
    print("All Day 4 backend API tests passed successfully!")
