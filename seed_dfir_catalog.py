import asyncio

from backend.core.database import AsyncSessionLocal
from database.seeders.framework_seeder import seed_catalog_frameworks


async def main():
    async with AsyncSessionLocal() as db:
        try:
            await seed_catalog_frameworks(db)
            await db.commit()
            print("Frameworks and baseline controls seeded successfully")
        except Exception:
            await db.rollback()
            raise


asyncio.run(main())
