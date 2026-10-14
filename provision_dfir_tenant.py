import asyncio
from uuid import UUID

from backend.core.database import AsyncSessionLocal
from backend.services.provisioning import provision_tenant

TENANT_ID = UUID("ad5ccc2e-209d-441c-ac6d-a47bcccb8e66")

async def main():
    async with AsyncSessionLocal() as db:
        try:
            result = await provision_tenant(TENANT_ID, db)
            await db.commit()
            print(result)
        except Exception:
            await db.rollback()
            raise

asyncio.run(main())
