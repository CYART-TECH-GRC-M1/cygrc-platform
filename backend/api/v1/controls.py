from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.models.control import Control, Framework
from backend.schemas.control import ControlCreate, ControlResponse, ControlUpdate

router = APIRouter(prefix="/api/v1", tags=["controls"])


def get_tenant_id(x_tenant_id: Annotated[str | None, Header(alias="X-Tenant-ID")] = None) -> str:
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-ID header is required.",
        )
    return x_tenant_id


@router.get("/controls", response_model=list[ControlResponse], status_code=status.HTTP_200_OK)
async def list_controls(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    result = await db.execute(
        select(Control).where(Control.tenant_id == tenant_id).order_by(Control.id)
    )
    controls = result.scalars().all()
    return [
        ControlResponse(
            id=control.id,
            tenant_id=control.tenant_id,
            framework_id=control.framework_id,
            name=control.name,
            description=control.description,
            status=control.status,
            owner=control.owner,
        )
        for control in controls
    ]


@router.post("/controls", response_model=ControlResponse, status_code=status.HTTP_201_CREATED)
async def create_control(
    payload: ControlCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    framework = await db.get(Framework, payload.framework_id)
    if framework is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Framework not found.")

    new_control = Control(
        tenant_id=tenant_id,
        framework_id=payload.framework_id,
        name=payload.name,
        description=payload.description,
        status=payload.status,
        owner=payload.owner,
    )
    db.add(new_control)
    await db.commit()
    await db.refresh(new_control)

    return ControlResponse(
        id=new_control.id,
        tenant_id=new_control.tenant_id,
        framework_id=new_control.framework_id,
        name=new_control.name,
        description=new_control.description,
        status=new_control.status,
        owner=new_control.owner,
    )


@router.put("/controls/{control_id}", response_model=ControlResponse, status_code=status.HTTP_200_OK)
async def update_control(
    control_id: int,
    payload: ControlUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    result = await db.execute(
        select(Control).where(Control.id == control_id, Control.tenant_id == tenant_id)
    )
    control = result.scalar_one_or_none()

    if control is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found for this tenant.",
        )

    if payload.name is not None:
        control.name = payload.name
    if payload.description is not None:
        control.description = payload.description
    if payload.status is not None:
        control.status = payload.status
    if payload.owner is not None:
        control.owner = payload.owner

    await db.commit()
    await db.refresh(control)

    return ControlResponse(
        id=control.id,
        tenant_id=control.tenant_id,
        framework_id=control.framework_id,
        name=control.name,
        description=control.description,
        status=control.status,
        owner=control.owner,
    )
