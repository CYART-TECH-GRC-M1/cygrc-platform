import sys
sys.path.insert(0, ".")
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

TENANT_ID = "00000000-0000-0000-0000-00000000000a"
HEADERS = {"X-Tenant-ID": TENANT_ID}


@pytest.fixture
def test_lab_asset():
    """Provisions an authorized lab test asset in the asset inventory."""
    payload = {
        "name": "Purple Team Isolated Lab Host",
        "asset_type": "SERVER",
        "ip_address": "10.0.99.15",
        "hostname": "purple-lab-srv01.local",
        "criticality": "LOW",
        "environment": "LAB",
        "exposure": "INTERNAL",
    }
    resp = client.post("/api/v1/assets", json=payload, headers=HEADERS)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_campaign_persistent_lifecycle_and_target_authorization(test_lab_asset):
    # 1. Create Red Team Campaign in PENDING_APPROVAL state
    camp_payload = {
        "name": "FY26 Q4 Purple Team Active Directory Simulation",
        "description": "Evaluate detection rules for credential access and execution",
        "objective": "Verify Wazuh and Sigma coverage for PowerShell and Discovery techniques",
        "authorized_scope": {
            "environments": ["LAB", "TEST"],
            "allowed_ip_ranges": ["10.0.99.0/24"],
            "allow_production": False,
        },
        "approved_targets": [test_lab_asset["asset_id"]],
        "status": "PLANNING",
        "approval_status": "PENDING_APPROVAL",
        "operator_id": "operator-sarah",
        "schedule_type": "MANUAL",
        "techniques_tested": ["T1059.001", "T1082", "T1053.005"],
        "technique_catalogue": ["T1059.001", "T1082", "T1053.005"],
    }
    create_resp = client.post("/api/v1/campaigns", json=camp_payload, headers=HEADERS)
    assert create_resp.status_code == 201, create_resp.text
    campaign = create_resp.json()
    campaign_id = campaign["campaign_id"]
    assert campaign["approval_status"] == "PENDING_APPROVAL"
    assert "%" in campaign["coverage_score"]

    # 2. Pre-execution authorization check: Execution must fail while campaign is unapproved
    exec_unapproved = client.post(
        f"/api/v1/campaigns/{campaign_id}/execute",
        json={"target_asset_ids": [test_lab_asset["asset_id"]]},
        headers=HEADERS,
    )
    assert exec_unapproved.status_code == 400
    assert "PENDING_APPROVAL" in exec_unapproved.json()["detail"]

    # 3. Approve campaign
    approval_resp = client.patch(
        f"/api/v1/campaigns/{campaign_id}/approval",
        json={"approval_status": "APPROVED", "approved_by": "ciso@cygrc.local"},
        headers=HEADERS,
    )
    assert approval_resp.status_code == 200
    assert approval_resp.json()["approval_status"] == "APPROVED"
    assert approval_resp.json()["approved_by"] == "ciso@cygrc.local"

    # 4. Target authorization check: Execution must fail if unapproved target is supplied
    exec_unapproved_target = client.post(
        f"/api/v1/campaigns/{campaign_id}/execute",
        json={"target_asset_ids": ["unregistered-random-server-999"]},
        headers=HEADERS,
    )
    assert exec_unapproved_target.status_code == 200
    # The job for the unregistered target returns an authorization error in errors list
    assert exec_unapproved_target.json()["failed_count"] > 0
    assert any("not registered" in err["error"] for err in exec_unapproved_target.json()["errors"])

    # 5. Execute campaign with approved target
    exec_resp = client.post(
        f"/api/v1/campaigns/{campaign_id}/execute",
        json={"target_asset_ids": [test_lab_asset["asset_id"]]},
        headers=HEADERS,
    )
    assert exec_resp.status_code == 200
    assert exec_resp.json()["executed_count"] >= 1
    assert exec_resp.json()["status"] == "ACTIVE"

    # 6. Verify jobs persisted
    jobs_resp = client.get(f"/api/v1/campaigns/{campaign_id}/jobs", headers=HEADERS)
    assert jobs_resp.status_code == 200
    jobs = jobs_resp.json()
    assert len(jobs) >= 1
    assert any(j["target_asset_id"] == test_lab_asset["asset_id"] for j in jobs)

    # 7. Cancel campaign
    cancel_resp = client.post(f"/api/v1/campaigns/{campaign_id}/cancel", headers=HEADERS)
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"


def test_atomic_red_team_runner_and_safety_guardrails(test_lab_asset):
    # 1. Query approved catalog
    cat_resp = client.get("/api/v1/redteam/atomic/catalog")
    assert cat_resp.status_code == 200
    catalog = cat_resp.json()
    assert len(catalog) >= 5
    assert any(c["technique_id"] == "T1059.001" for c in catalog)
    assert any(c["technique_id"] == "T1082" for c in catalog)

    # 2. Execute safe catalog test (T1082 - System Information Discovery)
    atomic_payload = {
        "technique_id": "T1082",
        "technique_name": "System Information Discovery",
        "target_asset_id": test_lab_asset["asset_id"],
        "executor": "powershell",
    }
    exec_resp = client.post("/api/v1/redteam/atomic/execute", json=atomic_payload, headers=HEADERS)
    assert exec_resp.status_code == 200, exec_resp.text
    data = exec_resp.json()
    assert data["status"] == "SUCCESS"
    assert data["technique_id"] == "T1082"
    assert data["target_asset_id"] == test_lab_asset["asset_id"]
    assert len(data["execution_hash"]) == 64
    assert "[Atomic Red Team Controlled Runner" in data["execution_log"]

    # 3. Verify execution was persisted in DB
    hist_resp = client.get("/api/v1/redteam/atomic/history", headers=HEADERS)
    assert hist_resp.status_code == 200
    history = hist_resp.json()
    assert any(h["execution_id"] == data["execution_id"] for h in history)

    # 4. Safety Guardrail: Command injection / destructive command must be strictly rejected
    dangerous_payload = {
        "technique_id": "T1059.001",
        "technique_name": "PowerShell",
        "target_asset_id": test_lab_asset["asset_id"],
        "command": "powershell.exe -Command \"format c: /fs:ntfs /q\"",
    }
    danger_resp = client.post("/api/v1/redteam/atomic/execute", json=dangerous_payload, headers=HEADERS)
    assert danger_resp.status_code == 400
    assert "prohibited pattern" in danger_resp.json()["detail"].lower()


def test_target_authorization_blocks_production_asset():
    # 1. Provision a PRODUCTION asset
    prod_asset_resp = client.post(
        "/api/v1/assets",
        json={
            "name": "Live Core Production Database",
            "asset_type": "DATABASE",
            "ip_address": "172.16.0.5",
            "hostname": "prod-db01.corp.internal",
            "criticality": "CRITICAL",
            "environment": "PROD",
        },
        headers=HEADERS,
    )
    assert prod_asset_resp.status_code == 201
    prod_asset_id = prod_asset_resp.json()["asset_id"]

    # 2. Attempt to run Atomic Red Team test against PRODUCTION asset without scope override
    atomic_payload = {
        "technique_id": "T1082",
        "technique_name": "System Information Discovery",
        "target_asset_id": prod_asset_id,
        "executor": "powershell",
    }
    resp = client.post("/api/v1/redteam/atomic/execute", json=atomic_payload, headers=HEADERS)
    assert resp.status_code == 400
    assert "production" in resp.json()["detail"].lower()


def test_caldera_client_lifecycle_and_results_verification(test_lab_asset):
    # 1. Health check
    health_resp = client.get("/api/v1/redteam/caldera/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert health_data["status"] in ["UP", "UNREACHABLE", "DEGRADED"]

    # 2. Profiles catalogue
    prof_resp = client.get("/api/v1/redteam/caldera/profiles")
    assert prof_resp.status_code == 200
    profiles = prof_resp.json()
    assert len(profiles) >= 3
    assert any(p["adversary_id"] == "adv-discovery-01" for p in profiles)

    # 3. Rejection of unapproved adversary profile
    invalid_op = client.post(
        "/api/v1/redteam/caldera/operations",
        json={
            "name": "Illegal Profile Test",
            "adversary_id": "malicious-unapproved-payload-99",
            "target_asset_id": test_lab_asset["asset_id"],
        },
        headers=HEADERS,
    )
    assert invalid_op.status_code == 400
    assert "not in approved catalogue" in invalid_op.json()["detail"]

    # 4. Create approved Caldera operation
    op_payload = {
        "name": "Automated Host Discovery Operation",
        "adversary_id": "adv-discovery-01",
        "target_asset_id": test_lab_asset["asset_id"],
        "operator_id": "caldera-lead",
    }
    create_op = client.post("/api/v1/redteam/caldera/operations", json=op_payload, headers=HEADERS)
    assert create_op.status_code == 201, create_op.text
    op_data = create_op.json()
    op_id = op_data["operation_id"]
    assert op_data["adversary_id"] == "adv-discovery-01"

    # 5. Poll operation status
    poll_resp = client.get(f"/api/v1/redteam/caldera/operations/{op_id}", headers=HEADERS)
    assert poll_resp.status_code == 200
    assert poll_resp.json()["status"] in ["RUNNING", "COMPLETED"]

    # 6. Retrieve task results (evaluates individual tasks)
    results_resp = client.get(f"/api/v1/redteam/caldera/operations/{op_id}/results", headers=HEADERS)
    assert results_resp.status_code == 200
    results = results_resp.json()
    assert results["total_tasks"] >= 1
    assert results["overall_status"] in ["SUCCESS", "FAILED", "PARTIAL_FAILURE"]
    assert len(results["tasks"]) >= 1

    # 7. Cancel operation
    cancel_resp = client.post(f"/api/v1/redteam/caldera/operations/{op_id}/cancel", headers=HEADERS)
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"


def test_mitre_attack_matrix_and_dynamic_coverage():
    # 1. Matrix endpoint returns v19.1
    resp = client.get("/api/v1/mitre/matrix")
    assert resp.status_code == 200
    matrix = resp.json()
    assert matrix["version"] == "MITRE ATT&CK v19.1"
    assert matrix["total_tactics"] == 15
    assert matrix["total_techniques_mapped"] >= 25

    # 2. Technique lookup
    t1059 = client.get("/api/v1/mitre/techniques/T1059.001")
    assert t1059.status_code == 200
    assert t1059.json()["technique_name"] == "PowerShell"

    # 3. Invalid technique lookup
    invalid_tech = client.get("/api/v1/mitre/techniques/T9999.999")
    assert invalid_tech.status_code == 404


def test_detection_verification_purple_team_correlation(test_lab_asset):
    # 1. Execute Atomic test for T1059.001
    atomic_payload = {
        "technique_id": "T1059.001",
        "technique_name": "PowerShell",
        "target_asset_id": test_lab_asset["asset_id"],
        "executor": "powershell",
    }
    exec_resp = client.post("/api/v1/redteam/atomic/execute", json=atomic_payload, headers=HEADERS)
    assert exec_resp.status_code == 200
    exec_id = exec_resp.json()["execution_id"]

    # 2. Ingest matching SOC alert for T1059.001
    alert_payload = {
        "title": "Suspicious PowerShell Execution Detected [T1059.001]",
        "source": "Wazuh SIEM",
        "severity": "HIGH",
        "description": f"Rule 100201: Detected suspicious powershell on {test_lab_asset['name']}",
    }
    alert_resp = client.post("/api/v1/alerts", json=alert_payload, headers=HEADERS)
    assert alert_resp.status_code == 201

    # 3. Correlate execution with SOC alerts -> DETECTED
    verify_resp = client.post(
        "/api/v1/redteam/detection/verify",
        json={
            "execution_id": exec_id,
            "technique_id": "T1059.001",
            "target_asset_id": test_lab_asset["asset_id"],
        },
        headers=HEADERS,
    )
    assert verify_resp.status_code == 200
    v_data = verify_resp.json()
    assert v_data["status"] == "DETECTED"
    assert len(v_data["matched_alert_ids"]) >= 1
    assert len(v_data["detection_rules_fired"]) >= 1

    # 4. Correlate an untested technique without alerts -> GAP
    gap_verify_resp = client.post(
        "/api/v1/redteam/detection/verify",
        json={
            "execution_id": f"ART-GAP-{exec_id}",
            "technique_id": "T1048",
            "target_asset_id": test_lab_asset["asset_id"],
        },
        headers=HEADERS,
    )
    assert gap_verify_resp.status_code == 200
    gap_data = gap_verify_resp.json()
    assert gap_data["status"] == "GAP"

    # 5. Analyst manual verification
    manual_resp = client.post(
        "/api/v1/redteam/detection/manual-verify",
        json={
            "verification_id": gap_data["verification_id"],
            "analyst_name": "lead_soc_analyst@cygrc.local",
            "notes": "Confirmed gap: EDR sensor telemetry was not ingested for T1048.",
            "status": "MANUALLY_VERIFIED",
        },
        headers=HEADERS,
    )
    assert manual_resp.status_code == 200
    assert manual_resp.json()["status"] == "MANUALLY_VERIFIED"
    assert manual_resp.json()["verified_by"] == "lead_soc_analyst@cygrc.local"

    # 6. List detection gaps
    gaps_resp = client.get("/api/v1/redteam/detection/gaps", headers=HEADERS)
    assert gaps_resp.status_code == 200


def test_post_campaign_report_and_remediation_backlog(test_lab_asset):
    # 1. Create and execute campaign
    camp_payload = {
        "name": "Q4 Purple Team Assessment Exercise",
        "description": "Evaluate multi-stage detection coverage",
        "approved_targets": [test_lab_asset["asset_id"]],
        "techniques_tested": ["T1059.001", "T1082"],
        "approval_status": "APPROVED",
        "status": "ACTIVE",
    }
    create_resp = client.post("/api/v1/campaigns", json=camp_payload, headers=HEADERS)
    assert create_resp.status_code == 201
    camp_id = create_resp.json()["campaign_id"]

    # Execute
    client.post(
        f"/api/v1/campaigns/{camp_id}/execute",
        json={"target_asset_ids": [test_lab_asset["asset_id"]]},
        headers=HEADERS,
    )

    # 2. Generate Final Report
    rep_resp = client.post(f"/api/v1/campaigns/{camp_id}/generate-report", headers=HEADERS)
    assert rep_resp.status_code == 200, rep_resp.text
    rep_data = rep_resp.json()
    assert rep_data["campaign_id"] == camp_id
    assert rep_data["attack_matrix_version"] == "MITRE ATT&CK v19.1"
    assert rep_data["total_planned"] >= 2
    assert rep_data["total_executed"] >= 1
    assert "remediation_backlog" in rep_data
    assert isinstance(rep_data["remediation_backlog"], list)
    assert len(rep_data["executive_summary"]) > 20

    # 3. Retrieve latest report
    get_rep_resp = client.get(f"/api/v1/campaigns/{camp_id}/report", headers=HEADERS)
    assert get_rep_resp.status_code == 200
    assert get_rep_resp.json()["report_id"] == rep_data["report_id"]
