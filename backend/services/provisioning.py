"""Tenant auto-provisioning: seed catalog frameworks and baseline control mappings."""

import asyncio
import logging
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import AsyncSessionLocal
from backend.models.tenant import Tenant
from backend.models.tenant_control import TenantControlMapping
from database.seeders.framework_seeder import (
    get_baseline_controls_for_default_frameworks,
    get_default_frameworks,
    seed_catalog_frameworks,
)

logger = logging.getLogger(__name__)


def _empty_summary(tenant_id: UUID) -> Dict[str, Any]:
    return {
        "tenant_id": tenant_id,
        "frameworks_seeded": [],
        "mappings_created": 0,
        "mappings_skipped": 0,
    }


async def _existing_control_ids(db: AsyncSession, tenant_id: UUID) -> set:
    result = await db.execute(
        select(TenantControlMapping.control_id).where(
            TenantControlMapping.tenant_id == tenant_id
        )
    )
    return set(result.scalars().all())


async def _provision_with_session(tenant_id: UUID, db: AsyncSession) -> Dict[str, Any]:
    await seed_catalog_frameworks(db)

    tenant_res = await db.execute(select(Tenant).where(Tenant.tenant_id == tenant_id))
    tenant = tenant_res.scalars().first()
    if not tenant:
        logger.warning("Provisioning skipped: tenant %s not found", tenant_id)
        await db.commit()
        return _empty_summary(tenant_id)

    frameworks = await get_default_frameworks(db)
    controls = await get_baseline_controls_for_default_frameworks(db)
    existing_ids = await _existing_control_ids(db, tenant_id)

    created = 0
    skipped = 0
    for control in controls:
        if control.control_id in existing_ids:
            skipped += 1
            continue
        db.add(
            TenantControlMapping(
                tenant_id=tenant_id,
                control_id=control.control_id,
                status="ACTIVE",
            )
        )
        existing_ids.add(control.control_id)
        created += 1

    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        logger.info(
            "Provisioning unique constraint for tenant %s; treating as idempotent skip",
            tenant_id,
        )
        existing_ids = await _existing_control_ids(db, tenant_id)
        created = 0
        skipped = sum(1 for c in controls if c.control_id in existing_ids)

    return {
        "tenant_id": tenant_id,
        "frameworks_seeded": [fw.framework_name for fw in frameworks],
        "mappings_created": created,
        "mappings_skipped": skipped,
    }


async def provision_tenant(
    tenant_id: UUID, db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    Ensure default frameworks exist and inject baseline tenant control mappings.

    Idempotent. If the tenant is missing, logs and returns a no-op summary.
    When db is omitted, opens a dedicated AsyncSession (for background tasks).
    """
    if db is None:
        async with AsyncSessionLocal() as session:
            res = await _provision_with_session(tenant_id, session)
            await session.commit()
            return res
    res = await _provision_with_session(tenant_id, db)
    await db.flush()
    return res


async def run_tenant_provisioning(tenant_id: UUID) -> None:
    """Background-task entrypoint. Uses its own session; never fails the HTTP 201."""
    try:
        await asyncio.sleep(0.05)
        async with AsyncSessionLocal() as session:
            await provision_tenant(tenant_id, session)
            await session.commit()
    except Exception:
        logger.exception("Background provisioning failed for tenant %s", tenant_id)
