import sys
sys.path.insert(0, '.')
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

HEADERS = {"X-Tenant-ID": "00000000-0000-0000-0000-00000000000a"}


def test_team_a_ir_state_machine():
    # 1. Create case
    case_resp = client.post("/api/v1/cases", json={"title": "State Machine Test Case"}, headers=HEADERS)
    assert case_resp.status_code == 201
    case_id = case_resp.json()["case_id"]

    # 2. Valid transition: OPEN -> TRIAGED
    tr1 = client.post(f"/api/v1/cases/{case_id}/transition", json={"target_status": "TRIAGED"}, headers=HEADERS)
    assert tr1.status_code == 200, tr1.text
    assert tr1.json()["status"] == "TRIAGED"

    # 3. Invalid transition: TRIAGED -> REOPENED (Must return 400 Bad Request)
    tr2 = client.post(f"/api/v1/cases/{case_id}/transition", json={"target_status": "REOPENED"}, headers=HEADERS)
    assert tr2.status_code == 400


def test_team_b_jira_remediation_push():
    payload = {
        "cve_id": "CVE-2026-8888",
        "cvss_score": 9.5,
        "affected_product": "Authentication Server",
        "summary": "Critical authentication bypass vulnerability",
        "project_key": "CYGRC"
    }
    resp = client.post("/api/v1/vapt/jira/push", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["jira_ticket"]["ticket_key"].startswith("CYGRC-")
    assert data["jira_ticket"]["priority"] == "Highest"


def test_team_c_red_team_campaigns_and_heatmap():
    # 1. Create Red Team Campaign
    payload = {
        "name": "Q4 Enterprise Cyber Defense Exercise",
        "description": "Simulate APT29 adversary techniques against Active Directory",
        "techniques_tested": ["T1059.001", "T1003.001", "T1053.005", "T1566"]
    }
    resp = client.post("/api/v1/campaigns", json=payload, headers=HEADERS)
    assert resp.status_code == 201, resp.text
    camp_id = resp.json()["campaign_id"]

    # 2. Generate ATT&CK Coverage Heat Map
    hm_resp = client.get(f"/api/v1/campaigns/{camp_id}/heatmap", headers=HEADERS)
    assert hm_resp.status_code == 200, hm_resp.text
    hm_data = hm_resp.json()
    assert hm_data["techniques_tested_count"] == 4
    assert len(hm_data["heatmap"]) == 15


def test_team_d_ai_guardrails_human_approval():
    # 1. Generate AI draft
    draft_resp = client.post("/api/v1/ai/draft", json={"context_text": "Guardrails Test"}, headers=HEADERS)
    assert draft_resp.status_code == 200
    approval_token = draft_resp.json()["human_approval_token"]

    # 2. Human Sign-Off
    approve_resp = client.post("/api/v1/ai/approve", json={
        "human_approval_token": approval_token,
        "reviewer_email": "lead_analyst@cygrc.local"
    })
    # Approval must fail closed until draft persistence and reviewer
    # authentication are implemented; a caller-supplied email is not proof.
    assert approve_resp.status_code == 501, approve_resp.text
    assert "unavailable" in approve_resp.json()["detail"].lower()


if __name__ == "__main__":
    test_team_a_ir_state_machine()
    test_team_b_jira_remediation_push()
    test_team_c_red_team_campaigns_and_heatmap()
    test_team_d_ai_guardrails_human_approval()
    print("All Day 6 backend API tests passed successfully!")
