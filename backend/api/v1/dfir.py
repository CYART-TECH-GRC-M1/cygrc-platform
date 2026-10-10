from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.models.dfir import DfirChainOfCustody
from backend.models.evidence import Evidence
from backend.models.user import User
from backend.schemas.dfir import CustodyCreate, CustodyResponse


router = APIRouter()


def get_user_uuids(current_user: dict) -> tuple[UUID, UUID]:
    """Extract authenticated user and tenant IDs from the validated token."""
    try:
        user_id = UUID(str(current_user["user_id"]))
        tenant_id = UUID(str(current_user["tenant_id"]))
    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid user and tenant IDs are required in the authentication token.",
        )

    return user_id, tenant_id


async def set_tenant_context(db: AsyncSession, tenant_id: UUID) -> None:
    """Set PostgreSQL RLS context for the current transaction."""
    await db.execute(
        text("SELECT set_config('app.current_tenant', :tenant_id, true)"),
        {"tenant_id": str(tenant_id)},
    )


async def verify_access(
    db: AsyncSession,
    evidence_id: UUID,
    user_id: UUID,
    tenant_id: UUID,
) -> None:
    """Verify that both the authenticated user and evidence belong to this tenant."""
    user_result = await db.execute(
        select(User).where(
            User.user_id == user_id,
            User.tenant_id == tenant_id,
        )
    )
    if user_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authenticated user does not belong to this tenant.",
        )

    evidence_result = await db.execute(
        select(Evidence).where(
            Evidence.evidence_id == evidence_id,
            Evidence.tenant_id == tenant_id,
        )
    )
    if evidence_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found.",
        )


@router.post(
    "/evidence/{evidence_id}/custody",
    response_model=CustodyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a chain-of-custody event",
)
async def create_custody_record(
    evidence_id: UUID,
    payload: CustodyCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id, tenant_id = get_user_uuids(current_user)

    try:
        await set_tenant_context(db, tenant_id)
        await verify_access(db, evidence_id, user_id, tenant_id)

        record = DfirChainOfCustody(
            tenant_id=tenant_id,
            evidence_id=evidence_id,
            performed_by=user_id,
            action=payload.action,
            source=payload.source,
            destination=payload.destination,
            notes=payload.notes,
            integrity_hash=payload.integrity_hash,
        )

        db.add(record)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record

    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise


@router.get(
    "/evidence/{evidence_id}/custody",
    response_model=list[CustodyResponse],
    summary="Get evidence chain-of-custody history",
)
async def list_custody_records(
    evidence_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id, tenant_id = get_user_uuids(current_user)

    try:
        await set_tenant_context(db, tenant_id)
        await verify_access(db, evidence_id, user_id, tenant_id)

        result = await db.execute(
            select(DfirChainOfCustody)
            .where(
                DfirChainOfCustody.evidence_id == evidence_id,
                DfirChainOfCustody.tenant_id == tenant_id,
            )
            .order_by(DfirChainOfCustody.timestamp.asc())
        )
        return list(result.scalars().all())

    except HTTPException:
        await db.rollback()
        raise
