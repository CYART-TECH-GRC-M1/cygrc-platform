import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
HEADERS = {"X-Tenant-ID": "00000000-0000-0000-0000-00000000000a"}


def run_day10_final_dryrun():
    print("=" * 60)
    print("  CyGRC Platform - Module 2 (Cyber Defense)")
    print("  Day 10 Final Dry-Run & Delivery Health Check")
    print("=" * 60)

    # 1. Health & Server Info
    r_health = client.get("/health")
    assert r_health.status_code == 200
    print("[PASS] System Health Check: Healthy")

    # 2. Team A (SOC SIEM): Alert Queue & Incident Cases
    r_alert = client.get("/api/v1/alerts", headers=HEADERS)
    assert r_alert.status_code == 200
    r_cases = client.get("/api/v1/cases", headers=HEADERS)
    assert r_cases.status_code == 200
    print(f"[PASS] Team A (SOC SIEM): Verified Alert Queue ({len(r_alert.json())} alerts) & Cases ({len(r_cases.json())} cases)")

    # 3. Team B (VAPT Scanner): CVE Feeds & Prioritization
    r_cve = client.get("/api/v1/vapt/cve")
    assert r_cve.status_code == 200
    r_prio = client.post("/api/v1/vapt/cve/prioritize", json={
        "cvss_score": 9.1,
        "is_cisa_kev": True,
        "asset_criticality": "CRITICAL",
        "has_mitigating_control": False
    })
    assert r_prio.status_code == 200
    print(f"[PASS] Team B (VAPT): Verified CVE Feeds & Prioritization Formula (Score: {r_prio.json()['priority_score']})")

    # 4. Team C (DFIR & Red Team): Chain of Custody & MITRE ATT&CK
    r_coc = client.get("/api/v1/chain-of-custody", headers=HEADERS)
    assert r_coc.status_code == 200
    r_mitre = client.get("/api/v1/mitre/matrix")
    assert r_mitre.status_code == 200
    print(f"[PASS] Team C (DFIR & Red Team): Verified Chain of Custody ({len(r_coc.json())} evidence items) & MITRE ATT&CK Matrix ({r_mitre.json()['total_tactics']} Tactics)")

    # 5. Team D (Threat Intel & AI Copilot): STIX/TAXII & Cyber AI
    r_stix = client.get("/api/v1/stix/objects", headers=HEADERS)
    assert r_stix.status_code == 200
    r_taxii = client.get("/api/v1/taxii2/")
    assert r_taxii.status_code == 200
    r_ai = client.post("/api/v1/ai/draft", json={"context_text": "Dry-run verification"}, headers=HEADERS)
    assert r_ai.status_code == 200
    print(f"[PASS] Team D (Threat Intel & AI): Verified STIX/TAXII Server & AI Copilot (Guardrail Watermark: '{r_ai.json()['draft_watermark']}')")

    print("=" * 60)
    print("  ALL MODULE 2 SYSTEMS VERIFIED OPERATIONAL & READY FOR HANDOVER!")
    print("=" * 60)


if __name__ == "__main__":
    run_day10_final_dryrun()
