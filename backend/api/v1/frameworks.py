from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.models.control import Framework
from backend.schemas.control import FrameworkResponse

router = APIRouter(tags=["Frameworks"])


@router.get("/", response_model=List[FrameworkResponse], status_code=status.HTTP_200_OK)
async def list_frameworks(db: AsyncSession = Depends(get_db)):
    """
    List all compliance frameworks (ISO 27001, SOC 2, NIST, GDPR, PCI DSS, etc.).
    """
    result = await db.execute(select(Framework).order_by(Framework.framework_name))
    frameworks = result.scalars().all()
    return frameworks


@router.get("/{framework_id}", response_model=FrameworkResponse, status_code=status.HTTP_200_OK)
async def get_framework(framework_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Get specific compliance framework details by ID.
    """
    result = await db.execute(select(Framework).where(Framework.framework_id == framework_id))
    framework = result.scalar_one_or_none()
    if not framework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Framework not found"
        )
    return framework
