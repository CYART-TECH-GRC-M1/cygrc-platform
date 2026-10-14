
import sys
sys.path.insert(0, '.')

import pytest
import uuid
import asyncio
from fastapi.testclient import TestClient

from backend.main import app
from backend.core.database import AsyncSessionLocal
from backend.models.control import Framework, Control
from backend.models.tenant import TenantStatus
from backend.models.tenant_control import TenantControlMapping

client = TestClient(app)

HEADERS = {
    "X-Tenant-ID": "00000000-0000-0000-0000-00000000000a"
}


def test_team_a_case_to_forensics_handoff():
    # 1. Create incident case
    case_resp = client.post(
        "/api/v1/cases",
        json={"title": "Handoff Test Case"},
        headers=HEADERS,
    )
    assert case_resp.status_code == 201, case_resp.text
    case_id = case_resp.json()["case_id"]

    # 2. Trigger single-click handoff to DFIR Forensics
    handoff_payload = {
        "client_id": "C.9988776655443322",
        "artifact_name": "Windows.KapeFiles.Targets",
        "custodian_name": "DFIR Lead Analyst",
    }

    resp = client.post(
        f"/api/v1/cases/{case_id}/handoff-to-forensics",
        json=handoff_payload,
        headers=HEADERS,
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["evidence_id"].startswith("EVID-DFIR-")
    assert len(data["sha256_hash"]) == 64


def test_team_b_vapt_grc_evidence_feed():
    # Create a control and map it to the test tenant.
    async def seed_control_mapping():
        tenant_id = uuid.UUID(HEADERS["X-Tenant-ID"])
        control_id = uuid.uuid4()

        async with AsyncSessionLocal() as session:
            framework = Framework(
                framework_id=uuid.uuid4(),
                framework_name=f"ISO 27001 Day7 {uuid.uuid4().hex[:6]}",
                version="2022",
            )

            control = Control(
                control_id=control_id,
                framework_id=framework.framework_id,
                control_code="A.12.6.1",
                control_name="Technical Vulnerability Management",
                status=TenantStatus.ACTIVE,
            )

            mapping = TenantControlMapping(
                mapping_id=uuid.uuid4(),
                tenant_id=tenant_id,
                control_id=control_id,
                status="ACTIVE",
            )

            session.add(framework)
            session.add(control)
            session.add(mapping)
            await session.commit()

    asyncio.run(seed_control_mapping())

    # Send VAPT evidence to GRC.
    feed_payload = {
        "cve_id": "CVE-2026-7777",
        "cvss_score": 8.8,
        "affected_product": "Customer Portal Framework",
        "control_code": "A.12.6.1",
    }

    resp = client.post(
        "/api/v1/vapt/cve/evidence/feed-to-grc",
        json=feed_payload,
        headers=HEADERS,
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "SUCCESS", data
    assert data["evidence"]["control_code"] == "A.12.6.1"
    assert data["evidence"]["compliance_signal"] == "NON_COMPLIANT"


def test_team_c_dfir_investigation_timeline():
    resp = client.get(
        "/api/v1/chain-of-custody",
        headers=HEADERS,
    )
    assert resp.status_code == 200, resp.text
    trail = resp.json()
    assert isinstance(trail, list)


def test_team_d_ai_threat_analyzer_case_closure():
    closure_payload = {
        "case_id": "case-990011",
        "case_number": "INC-2026-9901",
        "title": "Phishing Incident Resolution",
        "alerts_count": 4,
    }

    resp = client.post(
        "/api/v1/ai/case-closure-summary",
        json=closure_payload,
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert "executive_summary" in data
    assert len(data["lessons_learned"]) >= 3


if __name__ == "__main__":
    test_team_a_case_to_forensics_handoff()
    test_team_b_vapt_grc_evidence_feed()
    test_team_c_dfir_investigation_timeline()
    test_team_d_ai_threat_analyzer_case_closure()
    print("All Day 7 backend API tests passed successfully!")
