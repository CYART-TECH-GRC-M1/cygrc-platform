from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.asset import Asset


class AssetDiscoveryService:
    """Ingests Nmap network scan results or Cloud VM discovery payloads."""

    @staticmethod
    async def process_nmap_discovery(
        scan_payload: Dict[str, Any],
        tenant_id: str,
        db: AsyncSession
    ) -> List[Asset]:
        """Parses scan payload and upserts tenant assets."""
        hosts = scan_payload.get("hosts", [])
        created_assets = []

        for host in hosts:
            ip = host.get("ip")
            hostname = host.get("hostname", f"host-{ip}")
            ports = host.get("open_ports", [])
            os_name = host.get("os", "Linux/Windows")

            # Determine criticality based on open ports
            criticality = "LOW"
            if 22 in ports or 3389 in ports or 443 in ports or 8443 in ports:
                criticality = "HIGH"
            if 53 in ports or 389 in ports or 636 in ports:  # DNS / Active Directory
                criticality = "CRITICAL"

            tags = [f"port-{p}" for p in ports]
            tags.append(os_name.lower())

            # Check if asset exists
            stmt = select(Asset).where(Asset.tenant_id == tenant_id, Asset.ip_address == ip)
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                existing.hostname = hostname
                existing.criticality = criticality
                existing.tags = list(set((existing.tags or []) + tags))
                created_assets.append(existing)
            else:
                asset = Asset(
                    tenant_id=tenant_id,
                    name=hostname,
                    asset_type="NETWORK" if "router" in os_name.lower() else "SERVER",
                    ip_address=ip,
                    hostname=hostname,
                    criticality=criticality,
                    status="ACTIVE",
                    tags=tags,
                )
                db.add(asset)
                created_assets.append(asset)

        await db.commit()
        return created_assets

    @staticmethod
    async def process_cloud_inventory(
        inventory_payload: Dict[str, Any],
        tenant_id: str,
        db: AsyncSession
    ) -> List[Asset]:
        """Ingests Cloud inventory instance lists (AWS / Azure / GCP)."""
        provider = inventory_payload.get("provider", "AWS").upper()
        instances = inventory_payload.get("instances", [])
        assets = []

        for inst in instances:
            instance_id = inst.get("instance_id", "inst-unknown")
            name = inst.get("name", instance_id)
            ip = inst.get("public_ip") or inst.get("private_ip")
            instance_type = inst.get("instance_type", "t3.medium")

            criticality = inst.get("criticality", "MEDIUM").upper()
            tags = inst.get("tags", [])
            tags.extend([provider.lower(), instance_type])

            stmt = select(Asset).where(Asset.tenant_id == tenant_id, Asset.hostname == name)
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                existing.ip_address = ip
                existing.criticality = criticality
                existing.tags = list(set((existing.tags or []) + tags))
                assets.append(existing)
            else:
                asset = Asset(
                    tenant_id=tenant_id,
                    name=name,
                    asset_type="CLOUD",
                    ip_address=ip,
                    hostname=name,
                    criticality=criticality,
                    status="ACTIVE",
                    tags=tags,
                )
                db.add(asset)
                assets.append(asset)

        await db.commit()
        return assets
