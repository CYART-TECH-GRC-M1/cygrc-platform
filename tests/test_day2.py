import sys
sys.path.insert(0, '.')
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

HEADERS = {"X-Tenant-ID": "00000000-0000-0000-0000-00000000000a"}


def test_team_a_sigma_and_wazuh():
    # 1. Test Sigma Rule Conversion
    sigma_yaml = """
title: Suspicious PowerShell Encoded Command
status: experimental
description: Detects base64 encoded command execution via PowerShell.
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\powershell.exe'
        CommandLine|contains: ' -e '
    condition: selection
level: high
"""
    resp = client.post("/api/v1/alerts/sigma/convert", json={"sigma_yaml": sigma_yaml})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["success"] is True
    assert "Sigma Rule: Detects base64" in data["wazuh_xml"]

    # 2. Test Wazuh Webhook Listener
    wazuh_event = {
        "rule": {
            "id": 5710,
            "level": 10,
            "description": "SSH brute force authentication failure limit exceeded"
        },
        "agent": {
            "id": "001",
            "name": "linux-app-01"
        },
        "full_log": "Oct 9 10:00:00 linux-app-01 sshd[1234]: Failed password for root from 198.51.100.99 port 22"
    }
    resp = client.post("/api/v1/alerts/wazuh/webhook", json=wazuh_event, headers=HEADERS)
    assert resp.status_code == 201, resp.text
    alert = resp.json()
    assert "Wazuh [linux-app-01]" in alert["title"]
    assert alert["severity"] == "HIGH"
    assert alert["source"] == "Wazuh SIEM Listener"


def test_team_b_asset_discovery():
    # 1. Test Nmap Discovery Pipeline
    nmap_payload = {
        "hosts": [
            {
                "ip": "10.0.1.50",
                "hostname": "db-primary-01.corp.local",
                "open_ports": [22, 5432],
                "os": "Ubuntu Linux 22.04"
            }
        ]
    }
    resp = client.post("/api/v1/assets/discover/nmap", json=nmap_payload, headers=HEADERS)
    assert resp.status_code == 200, resp.text
    assets = resp.json()
    assert len(assets) >= 1
    assert assets[0]["ip_address"] == "10.0.1.50"
    assert assets[0]["criticality"] == "HIGH"

    # 2. Test Cloud Inventory Pipeline
    cloud_payload = {
        "provider": "AWS",
        "instances": [
            {
                "instance_id": "i-0a1b2c3d4e5f6g7h8",
                "name": "aws-api-gateway",
                "public_ip": "54.210.10.20",
                "criticality": "CRITICAL",
                "tags": ["prod", "api"]
            }
        ]
    }
    resp = client.post("/api/v1/assets/discover/cloud", json=cloud_payload, headers=HEADERS)
    assert resp.status_code == 200, resp.text
    cloud_assets = resp.json()
    assert cloud_assets[0]["asset_type"] == "CLOUD"


def test_team_c_velociraptor_disabled_returns_503(monkeypatch):
    from backend.api.v1 import forensics as forensics_module
    from backend.services.velociraptor_service import VelociraptorServiceError

    def disabled_dispatch(*args, **kwargs):
        raise VelociraptorServiceError("Velociraptor integration is disabled.")

    monkeypatch.setattr(forensics_module, "dispatch_collection", disabled_dispatch)

    collect_payload = {
        "client_id": "C.1234567890abcdef",
        "artifact_name": "Windows.KapeFiles.Targets",
        "custodian_name": "Dr. Alan Grant",
        "custodian_email": "alan@cygrc.local",
        "parameters": {"Target": "AntivirusLogs"},
        "notes": "Emergency collection after malware alert.",
    }

    resp = client.post(
        "/api/v1/forensics/collect",
        json=collect_payload,
        headers=HEADERS,
    )

    assert resp.status_code == 503, resp.text
    assert "disabled" in resp.json()["detail"].lower()


def test_team_c_velociraptor_dispatch_returns_flow_id(monkeypatch):
    from backend.api.v1 import forensics as forensics_module

    monkeypatch.setattr(
        forensics_module,
        "dispatch_collection",
        lambda *args, **kwargs: "F.12345678",
    )

    collect_payload = {
        "client_id": "C.1234567890abcdef",
        "artifact_name": "Windows.KapeFiles.Targets",
        "custodian_name": "Dr. Alan Grant",
        "custodian_email": "alan@cygrc.local",
        "parameters": {"Target": "AntivirusLogs"},
        "notes": "Emergency collection after malware alert.",
    }

    resp = client.post(
        "/api/v1/forensics/collect",
        json=collect_payload,
        headers=HEADERS,
    )

    assert resp.status_code == 202, resp.text
    data = resp.json()
    assert data["collection_id"] == "F.12345678"
    assert data["status"] == "DISPATCHED"
    assert data["evidence_id"] is None
    assert data["sha256_hash"] is None
    assert data["chain_of_custody_id"] is None


def test_team_d_taxii2_server():
    # 1. Test TAXII Discovery
    resp = client.get("/api/v1/taxii2/")
    assert resp.status_code == 200
    assert "TAXII 2.1" in resp.json()["title"]

    # 2. Test STIX 2.1 Bundle Ingestion via TAXII 2.1
    bundle_payload = {
        "type": "bundle",
        "id": "bundle--11223344-5566-7788-9900-aabbccddeeff",
        "objects": [
            {
                "id": "indicator--99887766-5544-3322-1100-ffaaddeeccb",
                "type": "indicator",
                "name": "Malicious Domain Threat Feed",
                "description": "Phishing domain associated with APT29",
                "pattern": "[domain-name:value = 'malicious-phish.xyz']",
                "labels": ["phishing", "apt29"],
                "confidence": 95
            }
        ]
    }
    resp = client.post("/api/v1/taxii2/collections/default-threat-intel/objects/", json=bundle_payload, headers=HEADERS)
    assert resp.status_code == 202, resp.text
    assert resp.json()["objects_ingested"] == 1

    # 3. Test TAXII Objects Query
    query_resp = client.get("/api/v1/taxii2/collections/default-threat-intel/objects/?type=indicator", headers=HEADERS)
    assert query_resp.status_code == 200
    objs = query_resp.json()["objects"]
    assert any(o.get("id") == "indicator--99887766-5544-3322-1100-ffaaddeeccb" for o in objs)


if __name__ == "__main__":
    test_team_a_sigma_and_wazuh()
    test_team_b_asset_discovery()
    test_team_c_velociraptor_forensics()
    test_team_d_taxii2_server()
    print("All Day 2 backend API tests passed successfully!")



def test_forensic_job_status_hides_other_tenants(monkeypatch):
    from types import SimpleNamespace
    from backend.api.v1 import forensics as forensics_module
    from backend.core.dependencies import get_current_tenant_id, get_current_user
    from backend.core.database import get_db

    class FakeResult:
        def scalar_one_or_none(self):
            return None

    class FakeDB:
        async def execute(self, query):
            return FakeResult()

    async def fake_db():
        yield FakeDB()

    app = forensics_module.router
    from backend.main import app as main_app

    main_app.dependency_overrides[get_current_tenant_id] = (
        lambda: "tenant-b"
    )
    main_app.dependency_overrides[get_current_user] = (
        lambda: {"user_id": "user-b", "tenant_id": "tenant-b"}
    )
    main_app.dependency_overrides[get_db] = fake_db

    try:
        response = client.get(
            "/api/v1/forensics/jobs/job-owned-by-tenant-a",
            headers={"X-Tenant-ID": "tenant-b"},
        )
        assert response.status_code == 404, response.text
        assert response.json()["detail"] == "Forensic job not found."
    finally:
        main_app.dependency_overrides.pop(get_current_tenant_id, None)
        main_app.dependency_overrides.pop(get_current_user, None)
        main_app.dependency_overrides.pop(get_db, None)
