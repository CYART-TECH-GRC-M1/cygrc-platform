import sys
sys.path.insert(0, '.')
import pytest
import asyncio
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# Use dev tenant header for testing Day 1 endpoints
HEADERS = {"X-Tenant-ID": "00000000-0000-0000-0000-00000000000a"}


def test_alerts_crud():
    # 1. Ingest alert (Team A)
    payload = {
        "title": "Unauthorized SSH Access Attempt",
        "source": "Wazuh",
        "severity": "HIGH",
        "description": "Multiple failed SSH logins from suspicious IP 192.168.1.50",
        "raw_payload": {"rule_id": 5710, "attempts": 15}
    }
    resp = client.post("/api/v1/alerts", json=payload, headers=HEADERS)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["title"] == "Unauthorized SSH Access Attempt"
    assert data["status"] == "NEW"
    alert_id = data["alert_id"]

    # 2. List alerts
    resp = client.get("/api/v1/alerts", headers=HEADERS)
    assert resp.status_code == 200
    alerts = resp.json()
    assert any(a["alert_id"] == alert_id for a in alerts)

    # 3. Patch alert status
    resp = client.patch(f"/api/v1/alerts/{alert_id}", json={"status": "TRIAGED"}, headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["status"] == "TRIAGED"


def test_assets_crud():
    # 1. Create asset (Team B)
    payload = {
        "name": "Prod Web Server 01",
        "asset_type": "SERVER",
        "ip_address": "10.0.0.15",
        "hostname": "web-prod-01.local",
        "criticality": "HIGH",
        "tags": ["web", "production", "pci-dss"]
    }
    resp = client.post("/api/v1/assets", json=payload, headers=HEADERS)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["name"] == "Prod Web Server 01"
    asset_id = data["asset_id"]

    # 2. List assets
    resp = client.get("/api/v1/assets", headers=HEADERS)
    assert resp.status_code == 200
    assets = resp.json()
    assert any(a["asset_id"] == asset_id for a in assets)


def test_chain_of_custody_append_only():
    # 1. Append custody record (Team C)
    payload = {
        "evidence_id": "EVID-2026-0099",
        "item_description": "RAM Dump Image file memory.raw",
        "custodian_name": "Sarah Connor",
        "custodian_email": "sarah@cygrc.local",
        "action": "COLLECTED",
        "location": "Secure Storage Safe A",
        "hash_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "notes": "Acquired using Velociraptor endpoint agent."
    }
    resp = client.post("/api/v1/chain-of-custody", json=payload, headers=HEADERS)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["evidence_id"] == "EVID-2026-0099"
    custody_id = data["custody_id"]

    # 2. List custody records
    resp = client.get("/api/v1/chain-of-custody", headers=HEADERS)
    assert resp.status_code == 200
    records = resp.json()
    assert any(r["custody_id"] == custody_id for r in records)

    # 3. Attempt modification / deletion (Must return 405 Method Not Allowed)
    resp_put = client.put(f"/api/v1/chain-of-custody/{custody_id}", json={"action": "TAMPERED"}, headers=HEADERS)
    assert resp_put.status_code == 405

    resp_del = client.delete(f"/api/v1/chain-of-custody/{custody_id}", headers=HEADERS)
    assert resp_del.status_code == 405


def test_stix_store():
    # 1. Store STIX 2.1 object (Team D)
    payload = {
        "type": "indicator",
        "name": "Malicious IP Indicator",
        "description": "Known Command & Control IP address",
        "pattern": "[ipv4-addr:value = '198.51.100.42']",
        "labels": ["malicious-activity", "c2"],
        "confidence": 85
    }
    resp = client.post("/api/v1/stix/objects", json=payload, headers=HEADERS)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["type"] == "indicator"
    stix_id = data["stix_id"]

    # 2. List STIX objects
    resp = client.get("/api/v1/stix/objects", headers=HEADERS)
    assert resp.status_code == 200
    objs = resp.json()
    assert any(o["stix_id"] == stix_id for o in objs)


if __name__ == "__main__":
    test_alerts_crud()
    test_assets_crud()
    test_chain_of_custody_append_only()
    test_stix_store()
    print("All Day 1 backend API tests passed successfully!")
