import sys
sys.path.insert(0, '.')
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

HEADERS = {"X-Tenant-ID": "00000000-0000-0000-0000-00000000000a"}


def test_team_a_soc_lead_signoff_enforcement():
    # 1. Create High severity case
    case_resp = client.post("/api/v1/cases", json={"title": "High Severity Signoff Test", "severity": "HIGH"}, headers=HEADERS)
    assert case_resp.status_code == 201
    case_id = case_resp.json()["case_id"]

    # 2. Attempt closure WITHOUT lead sign-off -> Must fail with 403 Forbidden
    close_attempt = client.post(f"/api/v1/cases/{case_id}/transition", json={"target_status": "CLOSED"}, headers=HEADERS)
    assert close_attempt.status_code == 403

    # 3. Provide SOC Lead sign-off
    signoff_payload = {
        "lead_email": "soc_lead@cygrc.local",
        "lead_notes": "Reviewed investigation logs and verified containment.",
        "signoff_approval_token": "SIGNOFF-TOKEN-LEAD-9988"
    }
    signoff_resp = client.post(f"/api/v1/cases/{case_id}/lead-signoff", json=signoff_payload, headers=HEADERS)
    assert signoff_resp.status_code == 200, signoff_resp.text

    # 4. Attempt closure WITH lead sign-off -> Must succeed
    close_success = client.post(f"/api/v1/cases/{case_id}/transition", json={"target_status": "CLOSED"}, headers=HEADERS)
    assert close_success.status_code == 200, close_success.text
    assert close_success.json()["status"] == "CLOSED"


def test_team_b_automated_scan_scheduling():
    sched_payload = {
        "asset_id": "asset-srv-01",
        "asset_name": "Production Database Server",
        "scan_type": "FULL_VAPT",
        "frequency": "DAILY"
    }
    resp = client.post("/api/v1/assets/scan-schedules", json=sched_payload, headers=HEADERS)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["schedule"]["schedule_id"].startswith("SCHED-")


def test_team_c_chain_of_custody_audit_export():
    resp = client.get("/api/v1/chain-of-custody/audit-export", headers=HEADERS)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "Official Audit Export Report" in data["export_title"]
    assert "integrity_seal" in data


def test_team_d_siem_control_bridge():
    bridge_payload = {
        "alert_id": "alert-siem-991",
        "title": "Wazuh: Multiple Failed SSH Logins",
        "severity": "HIGH",
        "control_id": "A.8.2"
    }
    resp = client.post("/api/v1/alerts/feed-control-evidence", json=bridge_payload, headers=HEADERS)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["control_signal"]["calculated_compliance_status"] == "NON_COMPLIANT"


if __name__ == "__main__":
    test_team_a_soc_lead_signoff_enforcement()
    test_team_b_automated_scan_scheduling()
    test_team_c_chain_of_custody_audit_export()
    test_team_d_siem_control_bridge()
    print("All Day 8 backend API tests passed successfully!")
