import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select

from backend.core.database import AsyncSessionLocal, engine
from backend.main import app
from backend.models.control import Control, Framework
from backend.models.tenant import Tenant
from backend.models.tenant_control import TenantControlMapping
from backend.services.provisioning import provision_tenant
from database.seeders.framework_seeder import seed_catalog_frameworks


async def _count_default_frameworks(db) -> int:
    result = await db.execute(
        select(func.count())
        .select_from(Framework)
        .where(Framework.framework_name.in_(["ISO 27001", "SOC 2"]))
    )
    return int(result.scalar_one())


async def _mapped_controls(db, tenant_id):
    result = await db.execute(
        select(TenantControlMapping, Control)
        .join(Control, TenantControlMapping.control_id == Control.control_id)
        .where(TenantControlMapping.tenant_id == tenant_id)
    )
    return result.all()


@pytest.mark.anyio
async def test_seeder_is_idempotent():
    async with AsyncSessionLocal() as db:
        await seed_catalog_frameworks(db)
        await db.commit()
        first = await _count_default_frameworks(db)

        await seed_catalog_frameworks(db)
        await db.commit()
        second = await _count_default_frameworks(db)

        iso = await db.execute(
            select(Control).where(
                Control.control_code.in_(["A.5.1", "A.8.2", "CC1.1", "CC6.1"])
            )
        )
        codes = {c.control_code for c in iso.scalars().all()}

    await engine.dispose()
    assert first == second
    assert first >= 2
    assert "A.5.1" in codes
    assert "A.8.2" in codes
    assert "CC1.1" in codes
    assert "CC6.1" in codes


@pytest.mark.anyio
async def test_provision_tenant_creates_access_control_and_security_policy_mappings():
    async with AsyncSessionLocal() as db:
        tenant = Tenant(
            name="Provision Test Co",
            domain=f"prov-{uuid.uuid4().hex[:12]}.example",
            subscription_plan="FREE",
        )
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)
        tenant_id = tenant.tenant_id

        summary = await provision_tenant(tenant_id, db)
        rows = await _mapped_controls(db, tenant_id)
        blob = " ".join(control.control_name for _, control in rows).lower()
        mapping_count = len(rows)

    await engine.dispose()
    assert summary["mappings_created"] >= 1
    assert "iso 27001" in [n.lower() for n in summary["frameworks_seeded"]] or summary[
        "frameworks_seeded"
    ]
    assert "access control" in blob
    assert "security policies" in blob or "security policy" in blob
    assert mapping_count >= 2


@pytest.mark.anyio
async def test_provision_tenant_second_run_does_not_duplicate_mappings():
    async with AsyncSessionLocal() as db:
        tenant = Tenant(
            name="Idempotent Provision Co",
            domain=f"prov2-{uuid.uuid4().hex[:12]}.example",
            subscription_plan="FREE",
        )
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)
        tenant_id = tenant.tenant_id

        first = await provision_tenant(tenant_id, db)
        count_after_first = (
            await db.execute(
                select(func.count())
                .select_from(TenantControlMapping)
                .where(TenantControlMapping.tenant_id == tenant_id)
            )
        ).scalar_one()

        second = await provision_tenant(tenant_id, db)
        count_after_second = (
            await db.execute(
                select(func.count())
                .select_from(TenantControlMapping)
                .where(TenantControlMapping.tenant_id == tenant_id)
            )
        ).scalar_one()

    await engine.dispose()
    assert count_after_first == count_after_second
    assert second["mappings_created"] == 0
    assert second["mappings_skipped"] == first["mappings_created"] or second[
        "mappings_skipped"
    ] == count_after_first


@pytest.mark.anyio
async def test_create_tenant_returns_201_and_provision_creates_mappings():
    domain = f"acme-{uuid.uuid4().hex[:12]}.example"
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/api/v1/tenants/",
            json={
                "name": "Acme Corp",
                "domain": domain,
                "subscription_plan": "FREE",
            },
        )

    assert response.status_code == 201
    body = response.json()
    tenant_id = uuid.UUID(body["tenant_id"])

    async with AsyncSessionLocal() as db:
        summary = await provision_tenant(tenant_id, db)
        rows = await _mapped_controls(db, tenant_id)
        blob = " ".join(control.control_name for _, control in rows).lower()

    await engine.dispose()
    assert summary["tenant_id"] == tenant_id
    assert len(rows) >= 1
    assert "access control" in blob
    assert "security policies" in blob or "security policy" in blob
