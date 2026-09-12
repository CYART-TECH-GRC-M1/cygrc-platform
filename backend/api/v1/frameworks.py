from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.models.control import Control, Framework
from backend.schemas.control import (
    ControlResponse,
    FrameworkCreate,
    FrameworkResponse,
)

router = APIRouter(tags=["Frameworks"])


@router.get("/", response_model=List[FrameworkResponse], status_code=status.HTTP_200_OK)
async def list_frameworks(db: AsyncSession = Depends(get_db)):
    """
    List all compliance frameworks (ISO 27001, SOC 2, NIST, GDPR, PCI DSS, etc.).
    """
    result = await db.execute(select(Framework).order_by(Framework.framework_name))
    frameworks = result.scalars().all()
    return frameworks


@router.post("/", response_model=FrameworkResponse, status_code=status.HTTP_201_CREATED)
async def create_framework(
    payload: FrameworkCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new compliance framework in the platform catalog.
    """
    existing_res = await db.execute(
        select(Framework).where(Framework.framework_name == payload.framework_name)
    )
    if existing_res.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Framework with name '{payload.framework_name}' already exists."
        )

    new_framework = Framework(
        framework_name=payload.framework_name,
        version=payload.version,
        description=payload.description,
    )
    db.add(new_framework)
    await db.commit()
    await db.refresh(new_framework)
    return new_framework


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


@router.get("/{framework_id}/controls", response_model=List[ControlResponse], status_code=status.HTTP_200_OK)
async def list_framework_controls(framework_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    List all controls under a specific framework.
    """
    framework_res = await db.execute(
        select(Framework).where(Framework.framework_id == framework_id)
    )
    if not framework_res.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Framework not found"
        )

    result = await db.execute(
        select(Control)
        .where(Control.framework_id == framework_id)
        .order_by(Control.control_code)
    )
    controls = result.scalars().all()
    return controls
