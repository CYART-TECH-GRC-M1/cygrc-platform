from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.controls import get_tenant_id
from backend.core.database import get_db
from backend.models.control import Framework
from backend.schemas.control import FrameworkResponse

router = APIRouter(prefix="/api/v1", tags=["frameworks"])


async def ensure_default_frameworks(db: AsyncSession) -> None:
    existing = await db.execute(select(Framework.name))
    existing_names = {name for (name,) in existing.all()}
    defaults = [
        {
            "name": "ISO 27001",
            "description": "Information Security Management System framework.",
            "category": "compliance",
            "is_default": True,
        },
        {
            "name": "SOC 2",
            "description": "Trust Services framework built around security, availability, processing integrity, confidentiality, and privacy.",
            "category": "compliance",
            "is_default": True,
        },
    ]
    for data in defaults:
        if data["name"] not in existing_names:
            db.add(Framework(**data))
    await db.commit()


@router.get("/frameworks", response_model=list[FrameworkResponse], status_code=status.HTTP_200_OK)
async def list_frameworks(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    del tenant_id
    await ensure_default_frameworks(db)
    result = await db.execute(select(Framework).where(Framework.is_default.is_(True)).order_by(Framework.id))
    frameworks = result.scalars().all()
    return [
        FrameworkResponse(
            id=framework.id,
            name=framework.name,
            description=framework.description,
            category=framework.category,
            is_default=framework.is_default,
        )
        for framework in frameworks
    ]
