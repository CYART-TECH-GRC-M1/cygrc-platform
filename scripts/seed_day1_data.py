import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.database import AsyncSessionLocal
from backend.models.alert import Alert
from backend.models.asset import Asset
from backend.models.chain_of_custody import ChainOfCustody
from backend.models.stix_object import StixObject

DEV_TENANT_ID = "00000000-0000-0000-0000-00000000000a"


async def seed_data():
    async with AsyncSessionLocal() as session:
        print("Seeding Day 1 Cyber Defense sample data...")

        # 1. Seed SOC SIEM Alerts (Team A)
        alert1 = Alert(
            tenant_id=DEV_TENANT_ID,
            title="Wazuh: Multiple Failed SSH Login Attempts",
            source="Wazuh SIEM",
            severity="HIGH",
            status="NEW",
            description="15 brute-force SSH authentication failures detected from external IP 198.51.100.42 targeting admin user.",
            raw_payload={"rule_id": 5710, "src_ip": "198.51.100.42", "agent_name": "linux-prod-db-01", "attempts": 15}
        )
        alert2 = Alert(
            tenant_id=DEV_TENANT_ID,
            title="Sigma: Encoded PowerShell Command Execution",
            source="Sigma Engine",
            severity="CRITICAL",
            status="TRIAGED",
            description="Execution of base64-encoded PowerShell script downloading remote payload from untrusted domain.",
            raw_payload={"rule_id": "sysmon_powershell_enc", "command": "powershell.exe -e aHR0cHM6Ly9ldmlsLnh5eg==", "host": "win-dc-01"}
        )
        session.add_all([alert1, alert2])

        # 2. Seed VAPT Scanner Assets (Team B)
        asset1 = Asset(
            tenant_id=DEV_TENANT_ID,
            name="Primary Domain Controller",
            asset_type="SERVER",
            ip_address="10.0.0.10",
            hostname="win-dc-01.corp.local",
            criticality="CRITICAL",
            status="ACTIVE",
            tags=["active-directory", "windows", "pci-dss"]
        )
        asset2 = Asset(
            tenant_id=DEV_TENANT_ID,
            name="Customer Portal Web App",
            asset_type="WEB_APP",
            ip_address="10.0.4.88",
            hostname="portal.cygrc.com",
            criticality="HIGH",
            status="ACTIVE",
            tags=["nextjs", "aws", "public-facing"]
        )
        session.add_all([asset1, asset2])

        # 3. Seed Chain of Custody Entries (Team C)
        coc1 = ChainOfCustody(
            tenant_id=DEV_TENANT_ID,
            evidence_id="EVID-2026-0001",
            item_description="Disk Image memory_dump_win_dc_01.raw",
            custodian_name="Alex Mercer",
            custodian_email="alex.mercer@cygrc.local",
            action="COLLECTED",
            location="Forensic Vault A",
            hash_sha256="8f4e2c1b9a3d7e6f5c4b3a2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f",
            notes="Acquired live RAM capture using Velociraptor endpoint collector."
        )
        session.add(coc1)

        # 4. Seed STIX 2.1 Threat Intel Objects (Team D)
        stix1 = StixObject(
            stix_id="indicator--8e2e2d2b-1a2b-3c4d-5e6f-7a8b9c0d1e2f",
            tenant_id=DEV_TENANT_ID,
            type="indicator",
            spec_version="2.1",
            name="C2 Server IPv4 Indicator",
            description="Known Cobalt Strike Command and Control IPv4 node",
            pattern="[ipv4-addr:value = '198.51.100.42']",
            labels=["malicious-activity", "c2", "cobalt-strike"],
            confidence=90,
            raw_stix={"type": "indicator", "id": "indicator--8e2e2d2b-1a2b-3c4d-5e6f-7a8b9c0d1e2f", "confidence": 90}
        )
        session.add(stix1)

        await session.commit()
        print("Day 1 sample data successfully seeded!")

if __name__ == "__main__":
    asyncio.run(seed_data())
