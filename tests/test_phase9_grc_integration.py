
import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from datetime import datetime

from backend.main import app
from backend.core.database import AsyncSessionLocal
from backend.models.control import Framework, Control
from backend.models.incident_case import IncidentCase
from backend.models.tenant import TenantStatus
from backend.models.tenant_control import TenantControlMapping


@pytest.mark.asyncio
async def test_risk_register_lifecycle(make_token):
    tenant_id = str(uuid.uuid4())
    token = make_token(tenant_id=tenant_id, role="Compliance Manager")
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": tenant_id,
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "title": "Unencrypted Database Backups",
            "description": "Daily database dumps are stored without encryption at rest.",
            "likelihood": 4,
            "impact": 5,
            "status": "ACTIVE",
        }
        resp = await client.post("/api/v1/risks", json=payload, headers=headers)
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["title"] == payload["title"]
        assert data["likelihood"] == 4
        assert data["impact"] == 5
        assert data["risk_score"] == 20
        risk_id = data["risk_id"]

        get_resp = await client.get(f"/api/v1/risks/{risk_id}", headers=headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["risk_id"] == risk_id

        assess_payload = {
            "likelihood": 2,
            "impact": 4,
            "comments": "Implemented AES-256 backup encryption; likelihood reduced.",
        }
        assess_resp = await client.post(
            f"/api/v1/risks/{risk_id}/assessments",
            json=assess_payload,
            headers=headers,
        )
        assert assess_resp.status_code == 201
        assert assess_resp.json()["risk_score"] == 8

        updated_risk = await client.get(
            f"/api/v1/risks/{risk_id}", headers=headers
        )
        assert updated_risk.json()["risk_score"] == 8
        assert updated_risk.json()["likelihood"] == 2

        treat_payload = {
            "treatment_plan": "Automate daily snapshot key rotation and verify restore.",
            "status": "OPEN",
        }
        treat_resp = await client.post(
            f"/api/v1/risks/{risk_id}/treatments",
            json=treat_payload,
            headers=headers,
        )
        assert treat_resp.status_code == 201
        assert treat_resp.json()["status"] == "OPEN"


@pytest.mark.asyncio
async def test_siem_control_bridge_persistence(make_token):
    tenant_id = str(uuid.uuid4())
    headers = {"X-Tenant-ID": tenant_id}

    ctrl_id = uuid.uuid4()
    async with AsyncSessionLocal() as session:
        fw = Framework(
            framework_id=uuid.uuid4(),
            framework_name=f"ISO 27001 Test {uuid.uuid4().hex[:6]}",
            version="2022",
        )
        ctrl = Control(
            control_id=ctrl_id,
            framework_id=fw.framework_id,
            control_code="A.5.1",
            control_name="Information Security Policies",
            status=TenantStatus.ACTIVE,
        )
        session.add(fw)
        session.add(ctrl)
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        alert_payload = {
            "alert_id": f"ALERT-{uuid.uuid4().hex[:6]}",
            "title": "Privilege Escalation Detected via Mimikatz",
            "severity": "CRITICAL",
            "control_id": "A.5.1",
        }
        resp = await client.post(
            "/api/v1/alerts/feed-control-evidence",
            json=alert_payload,
            headers=headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["status"] == "SUCCESS"
        assert data["persisted"] is True
        assert (
            data["control_signal"]["calculated_compliance_status"]
            == "NON_COMPLIANT"
        )


@pytest.mark.asyncio
async def test_vapt_evidence_and_risk_bridge(make_token):
    tenant_id = str(uuid.uuid4())
    headers = {"X-Tenant-ID": tenant_id}

    # Seed the framework, control, and tenant-specific active control mapping.
    ctrl_id = uuid.uuid4()
    async with AsyncSessionLocal() as session:
        fw = Framework(
            framework_id=uuid.uuid4(),
            framework_name=f"ISO 27001 VAPT {uuid.uuid4().hex[:6]}",
            version="2022",
        )
        ctrl = Control(
            control_id=ctrl_id,
            framework_id=fw.framework_id,
            control_code="A.12.6.1",
            control_name="Technical Vulnerability Management",
            status=TenantStatus.ACTIVE,
        )
        mapping = TenantControlMapping(
            mapping_id=uuid.uuid4(),
            tenant_id=uuid.UUID(tenant_id),
            control_id=ctrl_id,
            status="ACTIVE",
        )

        session.add(fw)
        session.add(ctrl)
        session.add(mapping)
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        vapt_payload = {
            "cve_id": "CVE-2024-3094",
            "cvss_score": 10.0,
            "affected_product": "xz-utils 5.6.0",
            "control_code": "A.12.6.1",
        }
        resp = await client.post(
            "/api/v1/vapt/cve/evidence/feed-to-grc",
            json=vapt_payload,
            headers=headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["status"] == "SUCCESS", data
        assert data["evidence"]["compliance_signal"] == "NON_COMPLIANT"
        assert data["evidence"]["persisted_evidence"] is True
        assert data["evidence"]["created_risk_id"] is not None

        token = make_token(tenant_id=tenant_id, role="Compliance Manager")
        auth_headers = {
            "Authorization": f"Bearer {token}",
            "X-Tenant-ID": tenant_id,
        }
        risk_resp = await client.get(
            f"/api/v1/risks/{data['evidence']['created_risk_id']}",
            headers=auth_headers,
        )
        assert risk_resp.status_code == 200, risk_resp.text
        risk_data = risk_resp.json()
        assert "CVE-2024-3094" in risk_data["title"]
        assert risk_data["risk_score"] == 20


@pytest.mark.asyncio
async def test_incident_case_to_grc_export(make_token):
    tenant_id = str(uuid.uuid4())
    headers = {"X-Tenant-ID": tenant_id}

    ctrl_id = uuid.uuid4()
    async with AsyncSessionLocal() as session:
        fw = Framework(
            framework_id=uuid.uuid4(),
            framework_name=f"ISO 27001 Incident {uuid.uuid4().hex[:6]}",
            version="2022",
        )
        ctrl = Control(
            control_id=ctrl_id,
            framework_id=fw.framework_id,
            control_code="A.16.1.1",
            control_name="Responsibilities and procedures",
            status=TenantStatus.ACTIVE,
        )
        case = IncidentCase(
            case_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            case_number="INC-2026-TEST",
            title="Unauthorized AWS S3 Bucket Exfiltration",
            nist_phase="CONTAINMENT_ERADICATION_RECOVERY",
            severity="HIGH",
            status="RESOLVED",
            summary="S3 bucket policy revoked and credentials rotated.",
            alerts_linked=["ALERT-101", "ALERT-102"],
        )
        session.add(fw)
        session.add(ctrl)
        session.add(case)
        await session.commit()
        case_id = case.case_id

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/v1/cases/{case_id}/feed-to-grc?control_code=A.16.1.1",
            headers=headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["status"] == "SUCCESS"
        assert data["persisted"] is True
        assert data["case_number"] == "INC-2026-TEST"
        assert data["compliance_signal"] == "COMPLIANT"
