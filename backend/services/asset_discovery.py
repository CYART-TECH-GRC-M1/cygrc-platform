"""Asset Discovery and Inventory Reconciliation Service.

Features:
- Tenant-scoped uniqueness and stable asset identifiers.
- Duplicate asset detection and non-destructive reconciliation.
- Controlled live Nmap discovery invocation.
- Authenticated Cloud VM inventory discovery (AWS/Azure/GCP).
- Asset retirement and status management.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.audit import record_audit_log
from backend.models.asset import Asset
from backend.services.scanner_adapters import (
    CloudDiscoveryAdapters,
)

logger = logging.getLogger(__name__)


class AssetDiscoveryService:
    """Manages asset inventory lifecycle, live discovery, and duplicate reconciliation."""

    @classmethod
    async def process_nmap_discovery(
        cls,
        scan_payload: Dict[str, Any],
        tenant_id: str,
        db: AsyncSession,
    ) -> List[Asset]:
        """Parses scan payload and reconciles tenant assets without creating duplicates."""
        hosts = scan_payload.get("hosts", [])
        reconciled_assets = []
        now = datetime.now(timezone.utc)

        for host in hosts:
            ip = host.get("ip")
            hostname = host.get("hostname") or (f"host-{ip.replace('.', '-')}" if ip else "unnamed-host")
            ports = host.get("open_ports", [])
            os_name = host.get("os", "Linux/Windows")

            # Determine criticality based on exposed services
            criticality = "LOW"
            if any(p in ports for p in [22, 3389, 443, 8443]):
                criticality = "HIGH"
            if any(p in ports for p in [53, 389, 636, 88, 445]):  # DNS, AD, Kerberos, SMB
                criticality = "CRITICAL"

            tags = [f"port-{p}" for p in ports]
            if os_name:
                tags.append(os_name.lower().split()[0])

            # Deduplication: Match on (tenant_id, ip_address) OR (tenant_id, hostname)
            match_conds = []
            if ip:
                match_conds.append(Asset.ip_address == ip)
            if hostname:
                match_conds.append(Asset.hostname == hostname)

            existing = None
            if match_conds:
                stmt = select(Asset).where(Asset.tenant_id == tenant_id, or_(*match_conds))
                res = await db.execute(stmt)
                existing = res.scalars().first()

            if existing:
                # Reconcile existing record
                existing.hostname = hostname or existing.hostname
                existing.ip_address = ip or existing.ip_address
                existing.os_name = os_name
                # Reconcile criticality from current scan observation
                existing.criticality = criticality

                # Merge tags
                combined_tags = list(set((existing.tags or []) + tags))
                existing.tags = combined_tags
                existing.updated_at = now
                reconciled_assets.append(existing)
                logger.info("Reconciled existing asset %s (%s)", existing.asset_id, ip)
            else:
                # Create new asset
                new_asset = Asset(
                    tenant_id=tenant_id,
                    name=hostname,
                    asset_type="NETWORK" if "router" in os_name.lower() or "switch" in os_name.lower() else "SERVER",
                    ip_address=ip,
                    hostname=hostname,
                    criticality=criticality,
                    status="ACTIVE",
                    environment="PROD",
                    exposure="INTERNAL" if (ip and (ip.startswith("10.") or ip.startswith("192.168."))) else "EXTERNAL",
                    os_name=os_name,
                    tags=tags,
                )
                db.add(new_asset)
                reconciled_assets.append(new_asset)
                logger.info("Created new asset %s for tenant %s", hostname, tenant_id)

        await db.commit()
        for a in reconciled_assets:
            await db.refresh(a)

        return reconciled_assets

    @classmethod
    async def process_cloud_inventory(
        cls,
        inventory_payload: Dict[str, Any],
        tenant_id: str,
        db: AsyncSession,
    ) -> List[Asset]:
        """Ingests supplied cloud inventory payload (AWS / Azure / GCP) with deduplication."""
        provider = inventory_payload.get("provider", "AWS").upper()
        instances = inventory_payload.get("instances", [])
        assets = []
        now = datetime.now(timezone.utc)

        for inst in instances:
            instance_id = inst.get("instance_id", f"inst-{inst.get('name', 'unknown')}")
            name = inst.get("name", instance_id)
            ip = inst.get("public_ip") or inst.get("private_ip")
            instance_type = inst.get("instance_type", "t3.medium")
            criticality = inst.get("criticality", "MEDIUM").upper()

            tags = inst.get("tags", [])
            tags.extend([provider.lower(), instance_type])

            # Deduplication
            stmt = select(Asset).where(
                Asset.tenant_id == tenant_id,
                or_(Asset.hostname == name, Asset.name == name)
            )
            res = await db.execute(stmt)
            existing = res.scalars().first()

            if existing:
                existing.ip_address = ip or existing.ip_address
                existing.criticality = criticality
                existing.tags = list(set((existing.tags or []) + tags))
                existing.updated_at = now
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
                    environment="PROD",
                    exposure="EXTERNAL" if inst.get("public_ip") else "INTERNAL",
                    tags=tags,
                )
                db.add(asset)
                assets.append(asset)

        await db.commit()
        for a in assets:
            await db.refresh(a)

        return assets

    @classmethod
    async def run_live_cloud_discovery(
        cls,
        provider: str,
        tenant_id: str,
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """
        Executes live cloud discovery using provider adapters.
        Explicitly distinguishes real cloud discovery from supplied payload ingestion.
        """
        provider_norm = provider.upper()
        if provider_norm == "AWS":
            result = CloudDiscoveryAdapters.discover_aws()
        elif provider_norm == "AZURE":
            result = CloudDiscoveryAdapters.discover_azure()
        elif provider_norm == "GCP":
            result = CloudDiscoveryAdapters.discover_gcp()
        else:
            return {
                "success": False,
                "provider": provider,
                "status": "UNSUPPORTED_PROVIDER",
                "error": f"Provider '{provider}' is not supported. Use AWS, AZURE, or GCP.",
            }

        if result.get("status") == "SUCCESS" and result.get("instances"):
            reconciled = await cls.process_cloud_inventory(
                {"provider": provider_norm, "instances": result["instances"]},
                tenant_id=tenant_id,
                db=db,
            )
            return {
                "success": True,
                "provider": provider_norm,
                "status": "DISCOVERED",
                "instances_found": len(result["instances"]),
                "assets_reconciled": len(reconciled),
            }

        return {
            "success": False,
            "provider": provider_norm,
            "status": result.get("status", "PROVIDER_UNCONFIGURED"),
            "error": result.get("error", "No credentials or configuration available for live cloud discovery."),
        }

    @classmethod
    async def retire_asset(
        cls,
        asset_id: str,
        tenant_id: str,
        reason: str,
        db: AsyncSession,
    ) -> Asset:
        """Retires/decommissions an asset in an authorized manner."""
        stmt = select(Asset).where(Asset.asset_id == asset_id, Asset.tenant_id == tenant_id)
        res = await db.execute(stmt)
        asset = res.scalar_one_or_none()
        if not asset:
            raise LookupError(f"Asset '{asset_id}' not found.")

        asset.status = "RETIRED"
        asset.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(asset)

        await record_audit_log(
            action="asset:retire",
            tenant_id=tenant_id,
            resource_type="asset",
            resource_id=asset_id,
            details={"asset_name": asset.name, "reason": reason},
            db=db,
        )
        return asset
