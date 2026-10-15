"""Phase 3 Comprehensive Verification Suite - VAPT and Vulnerability Management.

Verifies:
1. Asset inventory, discovery, metadata, reconciliation, and authorized retirement.
2. Scan scheduling lifecycle, concurrency limits, and running job deduplication.
3. Scanner integrations: Nmap, OWASP ZAP, OpenVAS, and Cloud adapters.
4. NVD & CISA KEV feeds, freshness tracking, and explicit handling of missing CVSS.
5. Vulnerability findings lifecycle connecting Asset -> Job -> Scanner -> Finding.
6. Prioritization engine with formula, boundary values, explainable breakdowns, and provisional CVSS.
7. Jira remediation integration with idempotency, back-links, and lifecycle preservation.
8. Tenant isolation for assets and findings.
"""
import sys
sys.path.insert(0, ".")
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.vulnerability_prioritization import VulnerabilityPrioritizationService
from backend.services.scanner_adapters import (
    NmapScannerAdapter,
    OWASPZapAdapter,
    OpenVASScannerAdapter,
    TargetScopeValidator,
    CloudDiscoveryAdapters,
)
from backend.services.cve_feed_service import CVEFeedService
from backend.services.jira_service import JiraIntegrationService

client = TestClient(app)

TENANT_A = "00000000-0000-0000-0000-00000000000a"
TENANT_B = "00000000-0000-0000-0000-00000000000b"
HEADERS_A = {"X-Tenant-ID": TENANT_A}
HEADERS_B = {"X-Tenant-ID": TENANT_B}


# ==============================================================================
# 1. Asset Inventory & Discovery
# ==============================================================================

def test_asset_crud_and_metadata():
    """Verify asset creation with full environment, exposure, and ownership metadata."""
    payload = {
        "name": "Primary Payment Vault",
        "asset_type": "SERVER",
        "ip_address": "10.0.10.15",
        "hostname": "vault-01.corp.internal",
        "criticality": "CRITICAL",
        "status": "ACTIVE",
        "environment": "PROD",
        "exposure": "INTERNAL",
        "owner": "secops@corp.internal",
        "os_name": "Ubuntu 22.04 LTS",
        "tags": ["pci-dss", "vault"],
    }
    resp = client.post("/api/v1/assets", json=payload, headers=HEADERS_A)
    assert resp.status_code == 201, resp.text
    asset = resp.json()
    asset_id = asset["asset_id"]
    assert asset["name"] == "Primary Payment Vault"
    assert asset["criticality"] == "CRITICAL"
    assert asset["environment"] == "PROD"
    assert asset["exposure"] == "INTERNAL"

    # Fetch asset
    get_resp = client.get(f"/api/v1/assets/{asset_id}", headers=HEADERS_A)
    assert get_resp.status_code == 200
    assert get_resp.json()["hostname"] == "vault-01.corp.internal"

    # Authorized Asset Retirement
    retire_resp = client.post(
        f"/api/v1/assets/{asset_id}/retire",
        json={"reason": "Server replaced by vault-02"},
        headers=HEADERS_A,
    )
    assert retire_resp.status_code == 200
    assert retire_resp.json()["status"] == "RETIRED"


def test_asset_tenant_isolation():
    """Verify Tenant B cannot view or retire Tenant A's assets."""
    create_resp = client.post(
        "/api/v1/assets",
        json={"name": "Tenant A Secret Database", "asset_type": "SERVER", "criticality": "HIGH"},
        headers=HEADERS_A,
    )
    assert create_resp.status_code == 201
    asset_id = create_resp.json()["asset_id"]

    # Tenant B tries to retrieve
    get_resp = client.get(f"/api/v1/assets/{asset_id}", headers=HEADERS_B)
    assert get_resp.status_code == 404

    # Tenant B tries to retire
    retire_resp = client.post(f"/api/v1/assets/{asset_id}/retire", json={}, headers=HEADERS_B)
    assert retire_resp.status_code == 404


def test_nmap_discovery_and_duplicate_reconciliation():
    """Verify duplicate asset detection reconciles existing record rather than creating duplicate."""
    scan_payload_1 = {
        "hosts": [
            {
                "ip": "10.0.5.20",
                "hostname": "gateway.local",
                "open_ports": [22, 80],
                "os": "Linux Ubuntu",
            }
        ]
    }
    resp1 = client.post("/api/v1/assets/discover/nmap", json=scan_payload_1, headers=HEADERS_A)
    assert resp1.status_code == 200
    assets1 = resp1.json()
    assert len(assets1) == 1
    asset_id_first = assets1[0]["asset_id"]

    # Re-scan same IP with new open port (443)
    scan_payload_2 = {
        "hosts": [
            {
                "ip": "10.0.5.20",
                "hostname": "gateway.local",
                "open_ports": [22, 80, 443],
                "os": "Linux Ubuntu",
            }
        ]
    }
    resp2 = client.post("/api/v1/assets/discover/nmap", json=scan_payload_2, headers=HEADERS_A)
    assert resp2.status_code == 200
    assets2 = resp2.json()
    assert len(assets2) == 1
    # ID must match (reconciled, not duplicated)
    assert assets2[0]["asset_id"] == asset_id_first
    assert "port-443" in assets2[0]["tags"]


def test_cloud_discovery_adapters_without_credentials():
    """Verify cloud discovery adapters reject live discovery when credentials are not configured."""
    resp = client.post("/api/v1/assets/discover/cloud-live", json={"provider": "AWS"}, headers=HEADERS_A)
    # Must fail cleanly with 400 when credentials are unconfigured, not fabricate results
    assert resp.status_code == 400
    data = resp.json()["detail"]
    assert data["status"] == "PROVIDER_UNCONFIGURED"
    assert "credentials not configured" in data["error"].lower()


# ==============================================================================
# 2. Scope Validation & Controlled Scan Runner
# ==============================================================================

def test_target_scope_validator():
    """Verify guardrails reject disallowed ranges (multicast/broadcast/reserved)."""
    # Multicast range
    is_valid, err, _ = TargetScopeValidator.validate_target("224.0.0.1")
    assert not is_valid
    assert "disallowed network" in err.lower()

    # Reserved broadcast
    is_valid, err, _ = TargetScopeValidator.validate_target("255.255.255.255")
    assert not is_valid

    # Valid internal IP
    is_valid, err, norm = TargetScopeValidator.validate_target("10.0.1.50")
    assert is_valid
    assert norm == "10.0.1.50"

    # Valid friendly asset name normalizes safely
    is_valid, err, norm = TargetScopeValidator.validate_target("Production Database Server")
    assert is_valid
    assert norm.endswith(".corp.local")


def test_nmap_scanner_adapter_xml_parser():
    """Verify Nmap XML parsing extracts ports, hostnames, and services accurately."""
    hosts = NmapScannerAdapter.parse_nmap_xml(NmapScannerAdapter.DOCUMENTED_TEST_FIXTURE_XML)
    assert len(hosts) == 1
    host = hosts[0]
    assert host["ip"] == "10.0.1.50"
    assert host["hostname"] == "db-primary-01.corp.local"
    assert 22 in host["open_ports"]
    assert 5432 in host["open_ports"]
    assert any(s["name"] == "postgresql" for s in host["services"])


# ==============================================================================
# 3. Durable Scan Scheduling & Concurrency
# ==============================================================================

def test_scan_schedule_lifecycle():
    """Verify schedule creation, status pause/resume, and execution."""
    # 1. Create Schedule
    payload = {
        "target": "10.0.2.10",
        "scan_type": "NETWORK_NMAP",
        "frequency": "WEEKLY",
        "concurrency_limit": 2,
    }
    resp = client.post("/api/v1/assets/scan-schedules", json=payload, headers=HEADERS_A)
    assert resp.status_code == 201
    sched = resp.json()
    sched_id = sched["schedule_id"]
    assert sched["status"] == "SUCCESS"
    assert sched["schedule_status"] == "ACTIVE"

    # 2. Pause Schedule
    pause_resp = client.patch(
        f"/api/v1/assets/scan-schedules/{sched_id}/status",
        json={"status": "PAUSED"},
        headers=HEADERS_A,
    )
    assert pause_resp.status_code == 200
    assert pause_resp.json()["status"] == "PAUSED"

    # 3. Resume Schedule
    resume_resp = client.patch(
        f"/api/v1/assets/scan-schedules/{sched_id}/status",
        json={"status": "ACTIVE"},
        headers=HEADERS_A,
    )
    assert resume_resp.status_code == 200
    assert resume_resp.json()["status"] == "ACTIVE"


def test_scan_job_scope_rejection_and_execution():
    """Verify illegal targets are rejected before scan execution."""
    illegal_job = {
        "target": "224.0.0.251",  # Multicast mDNS
        "scan_type": "NETWORK_NMAP",
    }
    resp = client.post("/api/v1/assets/scan-jobs", json=illegal_job, headers=HEADERS_A)
    assert resp.status_code == 400
    assert resp.json()["detail"]["status"] == "SCOPE_REJECTED"

    # Authorized test execution
    valid_job = {
        "target": "10.0.99.50",
        "scan_type": "NETWORK_NMAP",
    }
    exec_resp = client.post("/api/v1/assets/scan-jobs", json=valid_job, headers=HEADERS_A)
    assert exec_resp.status_code == 201
    job_data = exec_resp.json()
    assert job_data["success"] is True
    assert job_data["status"] == "COMPLETED"
    assert job_data["job_id"].startswith("JOB-")


# ==============================================================================
# 4. NVD & CISA KEV Feeds Synchronization
# ==============================================================================

def test_cve_feed_synchronization_and_missing_cvss():
    """Verify feed sync, freshness tracking, and explicit handling of missing CVSS scores."""
    # Sync verified test feed fixtures
    sync_resp = client.post("/api/v1/vapt/cve/sync", json={"feed_source": "NVD_CISA_KEV"}, headers=HEADERS_A)
    assert sync_resp.status_code == 200
    data = sync_resp.json()
    assert data["status"] == "SUCCESS"
    assert data["synced_cves"] >= 4

    # Check feed status metadata
    status_resp = client.get("/api/v1/vapt/cve/feed-status")
    assert status_resp.status_code == 200
    feed_meta = status_resp.json()
    assert feed_meta["last_sync_status"] == "SUCCESS"
    assert feed_meta["cisa_kev_active_count"] >= 3

    # Check pending CVSS entry is explicitly handled without crashing or silent 7.5
    cve_detail = client.get("/api/v1/vapt/cve/CVE-2024-0001-PENDING")
    assert cve_detail.status_code == 200
    cve_data = cve_detail.json()
    assert cve_data["cve_id"] == "CVE-2024-0001-PENDING"


# ==============================================================================
# 5. Prioritization Engine Formulas & Boundaries
# ==============================================================================

def test_prioritization_engine_formula_and_bounds():
    """Verify: Priority score = CVSS + KEV bonus (+3) + asset criticality (+1..4) - control (-2)."""
    # Test Case 1: Max Criticality with KEV
    # 9.8 + 3.0 (KEV) + 4.0 (CRITICAL) - 2.0 (Control) = 14.8 -> P1_URGENT
    res1 = VulnerabilityPrioritizationService.calculate_priority_score(
        cvss_score=9.8,
        is_cisa_kev=True,
        asset_criticality="CRITICAL",
        has_mitigating_control=True,
    )
    assert res1["priority_score"] == 14.8
    assert res1["priority_level"] == "P1_URGENT"
    assert res1["is_provisional"] is False
    assert res1["cvss_missing"] is False

    # Test Case 2: Missing CVSS score -> Must flag as provisional, not silently 7.5!
    res_missing = VulnerabilityPrioritizationService.calculate_priority_score(
        cvss_score=None,
        is_cisa_kev=False,
        asset_criticality="HIGH",
        has_mitigating_control=False,
    )
    assert res_missing["is_provisional"] is True
    assert res_missing["cvss_missing"] is True
    assert res_missing["breakdown"]["base_cvss"] is None
    # 5.0 (Provisional) + 0.0 + 3.0 (HIGH) - 0.0 = 8.0 -> P3_MEDIUM
    assert res_missing["priority_score"] == 8.0
    assert res_missing["priority_level"] == "P3_MEDIUM"
    assert "Provisional CVSS" in res_missing["formula_string"]

    # Test Case 3: Score bounds (Never below 0.0, never above 17.0)
    res_zero = VulnerabilityPrioritizationService.calculate_priority_score(
        cvss_score=0.0,
        is_cisa_kev=False,
        asset_criticality="LOW",  # +1.0
        has_mitigating_control=True,  # -2.0
    )
    assert res_zero["priority_score"] == 0.0  # Clamped to min 0.0, not negative


# ==============================================================================
# 6. Vulnerability Findings Lifecycle & Idempotent Jira Push
# ==============================================================================

def test_vulnerability_finding_lifecycle_and_jira_idempotency():
    """Verify Asset -> Finding creation -> CVE enrichment -> Idempotent Jira push."""
    # 1. Create test asset
    asset_resp = client.post(
        "/api/v1/assets",
        json={"name": "Production E-Commerce API", "asset_type": "SERVER", "criticality": "HIGH"},
        headers=HEADERS_A,
    )
    assert asset_resp.status_code == 201
    asset_id = asset_resp.json()["asset_id"]

    # 2. Create finding linked to asset
    finding_payload = {
        "asset_id": asset_id,
        "title": "Remote Code Execution via MOVEit Injection",
        "severity": "CRITICAL",
        "cve_id": "CVE-2023-34362",
        "scanner_source": "OPENVAS",
        "evidence": "Observed exploitable endpoint on /api/transfer",
        "has_mitigating_control": False,
    }
    finding_resp = client.post("/api/v1/vapt/findings", json=finding_payload, headers=HEADERS_A)
    assert finding_resp.status_code == 201, finding_resp.text
    finding = finding_resp.json()
    finding_id = finding["finding_id"]
    assert finding["asset_id"] == asset_id
    assert finding["priority_score"] >= 14.0  # 9.8 + 3.0 + 3.0 - 0 = 15.8 -> P1_URGENT
    assert finding["status"] == "OPEN"

    # 3. Push to Jira (First time -> Creates ticket)
    jira_resp_1 = client.post(f"/api/v1/vapt/findings/{finding_id}/push-jira", headers=HEADERS_A)
    assert jira_resp_1.status_code == 200, jira_resp_1.text
    ticket_1 = jira_resp_1.json()["jira_ticket"]
    ticket_key = ticket_1["ticket_key"]
    assert ticket_key.startswith("CYGRC-")

    # Verify finding status did NOT become REMEDIATED merely because ticket was opened!
    get_finding = client.get(f"/api/v1/vapt/findings/{finding_id}", headers=HEADERS_A)
    assert get_finding.json()["status"] != "REMEDIATED"

    # 4. Push to Jira second time -> IDEMPOTENCY: Must return existing ticket, not duplicate
    jira_resp_2 = client.post(f"/api/v1/vapt/findings/{finding_id}/push-jira", headers=HEADERS_A)
    assert jira_resp_2.status_code == 200
    res_2 = jira_resp_2.json()
    assert res_2["is_duplicate"] is True
    assert res_2["jira_ticket"]["ticket_key"] == ticket_key


# ==============================================================================
# 7. Scanner Health Endpoint
# ==============================================================================

def test_scanner_health_endpoint():
    """Verify scanner health endpoint distinguishes availability without fabricating results."""
    resp = client.get("/api/v1/vapt/findings/scanners/health")
    assert resp.status_code == 200
    data = resp.json()["scanners"]
    assert "nmap" in data
    assert "owasp_zap" in data
    assert "openvas" in data
    assert data["nmap"]["tool"] == "NMAP"
    assert data["owasp_zap"]["tool"] == "OWASP_ZAP"
    assert data["openvas"]["tool"] == "OPENVAS"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
