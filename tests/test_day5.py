import sys
sys.path.insert(0, '.')
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

HEADERS = {"X-Tenant-ID": "00000000-0000-0000-0000-00000000000a"}


def test_team_a_sse_realtime_stream():
    resp = client.get("/api/v1/alerts/stream", headers=HEADERS)
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    assert "data: {" in resp.text


def test_team_b_vapt_findings_query():
    resp = client.get("/api/v1/vapt/cve")
    assert resp.status_code == 200
    cves = resp.json()
    assert isinstance(cves, list)


def test_team_c_mitre_attack_matrix():
    # 1. Fetch Matrix
    resp = client.get("/api/v1/mitre/matrix")
    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == "MITRE ATT&CK v19.1"
    assert data["total_tactics"] == 15
    assert len(data["matrix"]) == 15

    # 2. Fetch Technique Detail
    tech_resp = client.get("/api/v1/mitre/techniques/T1059.001")
    assert tech_resp.status_code == 200
    tech_data = tech_resp.json()
    assert tech_data["technique_name"] == "PowerShell"


def test_team_d_ai_soc_copilot():
    draft_payload = {
        "context_text": "Suspicious powershell execution with base64 encoded payload",
        "draft_type": "triage_questions"
    }
    resp = client.post("/api/v1/ai/draft", json=draft_payload, headers=HEADERS)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["is_draft"] is True
    assert data["draft_watermark"] == "DRAFT_SUBJECT_TO_HUMAN_APPROVAL"
    assert len(data["suggested_triage_questions"]) >= 3
    assert len(data["human_approval_token"]) > 10


if __name__ == "__main__":
    test_team_a_sse_realtime_stream()
    test_team_b_vapt_findings_query()
    test_team_c_mitre_attack_matrix()
    test_team_d_ai_soc_copilot()
    print("All Day 5 backend API tests passed successfully!")
