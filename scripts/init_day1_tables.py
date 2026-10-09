import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.database import engine, Base
import backend.models  # Ensures all models are registered with Base.metadata


async def init_tables():
    async with engine.begin() as conn:
        print("Creating Day 1 Cyber Defense tables if not present...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables initialized successfully!")

if __name__ == "__main__":
    asyncio.run(init_tables())
