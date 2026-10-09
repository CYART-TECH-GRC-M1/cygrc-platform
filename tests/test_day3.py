import sys
sys.path.insert(0, '.')
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

HEADERS = {"X-Tenant-ID": "00000000-0000-0000-0000-00000000000a"}


def test_team_a_nist_incident_cases():
    # 1. Create NIST SP 800-61 Incident Case
    case_payload = {
        "title": "Unexplained Outbound Traffic Spike to Suspicious IP",
        "nist_phase": "DETECTION_ANALYSIS",
        "severity": "HIGH",
        "status": "OPEN",
        "summary": "High volume exfiltration attempt detected by SOC SIEM listener.",
        "assigned_analyst": "Analyst Jane Doe",
        "alerts_linked": ["alert-001", "alert-002"]
    }
    resp = client.post("/api/v1/cases", json=case_payload, headers=HEADERS)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["case_number"].startswith("INC-2026-")
    assert data["nist_phase"] == "DETECTION_ANALYSIS"
    case_id = data["case_id"]

    # 2. List Cases
    resp = client.get("/api/v1/cases", headers=HEADERS)
    assert resp.status_code == 200
    cases = resp.json()
    assert any(c["case_id"] == case_id for c in cases)

    # 3. Transition NIST Phase to CONTAINMENT_ERADICATION_RECOVERY
    resp = client.patch(
        f"/api/v1/cases/{case_id}",
        json={"nist_phase": "CONTAINMENT_ERADICATION_RECOVERY", "status": "IN_PROGRESS"},
        headers=HEADERS
    )
    assert resp.status_code == 200
    assert resp.json()["nist_phase"] == "CONTAINMENT_ERADICATION_RECOVERY"


def test_team_b_cve_feeds():
    # 1. Sync daily NVD and CISA KEV feeds
    sync_payload = {
        "feed_source": "NVD_CISA_KEV",
        "entries": [
            {
                "cve_id": "CVE-2026-9999",
                "cvss_score": 9.8,
                "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                "cisa_kev": True,
                "summary": "Remote Code Execution in Web Application Framework",
                "remediation": "Upgrade to v2.4.1 immediately.",
                "affected_product": "CyGRC Web Framework"
            }
        ]
    }
    resp = client.post("/api/v1/vapt/cve/sync", json=sync_payload)
    assert resp.status_code == 200, resp.text
    assert resp.json()["cisa_kev_active_exploits"] == 1

    # 2. Query CISA KEV active exploits
    resp = client.get("/api/v1/vapt/cve?cisa_kev=true")
    assert resp.status_code == 200
    cves = resp.json()
    assert any(c["cve_id"] == "CVE-2026-9999" for c in cves)


def test_team_c_custody_transfer_signature():
    # 1. Append initial evidence record
    init_payload = {
        "evidence_id": "EVID-TRANSFER-TEST",
        "item_description": "Hard Drive SSD 1TB Serial #998877",
        "custodian_name": "Alice Johnson",
        "custodian_email": "alice@cygrc.local",
        "action": "COLLECTED",
        "location": "Evidence Room B",
        "hash_sha256": "11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff"
    }
    init_resp = client.post("/api/v1/chain-of-custody", json=init_payload, headers=HEADERS)
    assert init_resp.status_code == 201

    # 2. Record Custody Transfer with digital signature verification
    transfer_payload = {
        "evidence_id": "EVID-TRANSFER-TEST",
        "previous_custodian": "Alice Johnson",
        "new_custodian_name": "Bob Smith",
        "new_custodian_email": "bob@cygrc.local",
        "new_location": "DFIR Forensics Lab",
        "verification_hash_sha256": "11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff",
        "custodian_signature": "SIG-EC-9908123-VERIFIED",
        "transfer_reason": "Handover for malware forensic analysis"
    }
    resp = client.post("/api/v1/chain-of-custody/transfer", json=transfer_payload, headers=HEADERS)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["action"] == "TRANSFERRED"
    assert data["custodian_name"] == "Bob Smith"


def test_team_d_misp_and_opencti():
    # 1. Test MISP Event Sync
    misp_payload = {
        "misp_payload": {
            "Event": {
                "info": "APT28 Campaign Indicators",
                "Attribute": [
                    {
                        "type": "ip-dst",
                        "category": "Network activity",
                        "value": "203.0.113.199"
                    }
                ]
            }
        }
    }
    resp = client.post("/api/v1/intel/misp/sync", json=misp_payload, headers=HEADERS)
    assert resp.status_code == 200, resp.text
    assert resp.json()["stix_objects_ingested"] == 1

    # 2. Test OpenCTI GraphQL Sync
    opencti_payload = {
        "graphql_data": {
            "data": {
                "stixDomainObjects": [
                    {
                        "id": "malware--opencti-001",
                        "entity_type": "Malware",
                        "name": "Ransomware Variant X",
                        "description": "Crypto-ransomware targetting Windows endpoints",
                        "confidence": 95
                    }
                ]
            }
        }
    }
    resp = client.post("/api/v1/intel/opencti/query", json=opencti_payload, headers=HEADERS)
    assert resp.status_code == 200, resp.text
    assert resp.json()["opencti_entities_ingested"] == 1


if __name__ == "__main__":
    test_team_a_nist_incident_cases()
    test_team_b_cve_feeds()
    test_team_c_custody_transfer_signature()
    test_team_d_misp_and_opencti()
    print("All Day 3 backend API tests passed successfully!")
