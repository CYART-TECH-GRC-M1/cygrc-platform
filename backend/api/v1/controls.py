from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.models.control import Control, Framework
from backend.schemas.control import ControlCreate, ControlResponse, ControlUpdate

router = APIRouter(tags=["Controls"])


@router.get("/", response_model=List[ControlResponse], status_code=status.HTTP_200_OK)
async def list_controls(
    framework_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all controls, optionally filtered by framework_id.
    """
    query = select(Control)
    if framework_id:
        query = query.where(Control.framework_id == framework_id)
    query = query.order_by(Control.control_code)
    
    result = await db.execute(query)
    controls = result.scalars().all()
    return controls


@router.post("/", response_model=ControlResponse, status_code=status.HTTP_201_CREATED)
async def create_control(
    payload: ControlCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new compliance control under a framework.
    """
    framework_res = await db.execute(select(Framework).where(Framework.framework_id == payload.framework_id))
    framework = framework_res.scalar_one_or_none()
    if not framework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specified Framework not found"
        )

    new_control = Control(
        framework_id=payload.framework_id,
        control_code=payload.control_code,
        control_name=payload.control_name,
        description=payload.description,
        status=payload.status or "ACTIVE"
    )
    db.add(new_control)
    await db.commit()
    await db.refresh(new_control)
    return new_control


@router.get("/{control_id}", response_model=ControlResponse, status_code=status.HTTP_200_OK)
async def get_control(control_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Get control details by ID.
    """
    result = await db.execute(select(Control).where(Control.control_id == control_id))
    control = result.scalar_one_or_none()
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found"
        )
    return control


@router.put("/{control_id}", response_model=ControlResponse, status_code=status.HTTP_200_OK)
async def update_control(
    control_id: UUID,
    payload: ControlUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update control details.
    """
    result = await db.execute(select(Control).where(Control.control_id == control_id))
    control = result.scalar_one_or_none()
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found"
        )

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(control, key, value)

    await db.commit()
    await db.refresh(control)
    return control
