from typing import List
from uuid import UUID
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.models.control import Control, Framework
from backend.models.tenant import Tenant
from backend.models.tenant_control import TenantControlMapping
from backend.schemas.control import ProvisionSummary, TenantMappedControlResponse
from backend.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse
from backend.services.provisioning import provision_tenant, run_tenant_provisioning

router = APIRouter()


@router.post(
    "/",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a tenant",
    description=(
        "Create a tenant and enqueue background provisioning of default "
        "frameworks (ISO 27001:2022, SOC 2:2017) and baseline control mappings. "
        "Returns 201 immediately; provisioning failures are logged and do not fail this request."
    ),
)
async def create_tenant(
    tenant_in: TenantCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
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
    background_tasks.add_task(run_tenant_provisioning, new_tenant.tenant_id)
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


@router.post(
    "/{tenant_id}/provision",
    response_model=ProvisionSummary,
    status_code=status.HTTP_200_OK,
    summary="Retry tenant provisioning",
    description=(
        "Synchronously seed the shared framework catalog (if missing) and "
        "idempotently insert baseline tenant control mappings."
    ),
)
async def retry_tenant_provision(
    tenant_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Tenant).where(Tenant.tenant_id == tenant_id))
    tenant = result.scalars().first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found.",
        )
    return await provision_tenant(tenant_id, db)


@router.get(
    "/{tenant_id}/controls",
    response_model=List[TenantMappedControlResponse],
    status_code=status.HTTP_200_OK,
    summary="List tenant mapped controls",
    description="Join tenant_controls with catalog controls and frameworks for this tenant.",
)
async def list_tenant_controls(
    tenant_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    tenant_res = await db.execute(select(Tenant).where(Tenant.tenant_id == tenant_id))
    if not tenant_res.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found.",
        )

    result = await db.execute(
        select(TenantControlMapping, Control, Framework)
        .join(Control, TenantControlMapping.control_id == Control.control_id)
        .join(Framework, Control.framework_id == Framework.framework_id)
        .where(TenantControlMapping.tenant_id == tenant_id)
        .order_by(Framework.framework_name, Control.control_code)
    )
    rows = result.all()
    return [
        TenantMappedControlResponse(
            mapping_id=mapping.mapping_id,
            tenant_id=mapping.tenant_id,
            control_id=mapping.control_id,
            mapping_status=mapping.status,
            seeded_at=mapping.seeded_at,
            control_code=control.control_code,
            control_name=control.control_name,
            description=control.description,
            control_status=control.status,
            framework_id=framework.framework_id,
            framework_name=framework.framework_name,
            framework_version=framework.version,
        )
        for mapping, control, framework in rows
    ]


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
