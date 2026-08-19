from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.models.tenant import Tenant
from backend.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse

router = APIRouter()


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_in: TenantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register/Onboard a new company (tenant)."""
    if tenant_in.domain:
        result = await db.execute(select(Tenant).where(Tenant.domain == tenant_in.domain))
        existing_tenant = result.scalars().first()
        if existing_tenant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tenant with domain '{tenant_in.domain}' already exists."
            )

    new_tenant = Tenant(
        name=tenant_in.name,
        domain=tenant_in.domain,
        subscription_plan=tenant_in.subscription_plan or "FREE"
    )
    db.add(new_tenant)
    await db.commit()
    await db.refresh(new_tenant)
    return new_tenant


@router.get("/me", response_model=TenantResponse)
async def get_current_tenant(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """Fetch current tenant details using tenant security dependency."""
    try:
        tenant_uuid = UUID(current_tenant_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant ID format in header/token."
        )

    result = await db.execute(select(Tenant).where(Tenant.tenant_id == tenant_uuid))
    tenant = result.scalars().first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found."
        )
    return tenant


@router.get("/", response_model=List[TenantResponse])
async def list_tenants(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all registered tenants."""
    result = await db.execute(select(Tenant).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant_by_id(
    tenant_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get tenant profile by tenant_id."""
    result = await db.execute(select(Tenant).where(Tenant.tenant_id == tenant_id))
    tenant = result.scalars().first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found."
        )
    return tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    tenant_in: TenantUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update tenant information."""
    result = await db.execute(select(Tenant).where(Tenant.tenant_id == tenant_id))
    tenant = result.scalars().first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found."
        )

    update_data = tenant_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)

    await db.commit()
    await db.refresh(tenant)
    return tenant
