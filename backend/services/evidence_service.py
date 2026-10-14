import uuid
from typing import Optional, List, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from backend.models.evidence import Evidence
from backend.models.control import Control
from backend.models.tenant import TenantStatus
from backend.schemas.evidence import EvidenceCreate


class EvidenceService:
    @staticmethod
    def _to_uuid(val: Any) -> uuid.UUID:
        if isinstance(val, uuid.UUID):
            return val
        try:
            return uuid.UUID(str(val))
        except (ValueError, TypeError):
            return uuid.uuid5(uuid.NAMESPACE_DNS, str(val))

    @classmethod
    async def create_evidence(
        cls,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        uploaded_by: uuid.UUID,
        payload: EvidenceCreate,
    ) -> Evidence:
        ctrl = await db.get(Control, payload.control_id)
        if not ctrl:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Control {payload.control_id} does not exist"
            )

        status_enum = (
            TenantStatus(payload.status)
            if payload.status in TenantStatus.__members__
            else TenantStatus.ACTIVE
        )

        record = Evidence(
            tenant_id=tenant_id,
            control_id=payload.control_id,
            uploaded_by=uploaded_by,
            title=payload.title,
            description=payload.description,
            status=status_enum,
            uploaded_at=datetime.utcnow(),
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    @classmethod
    async def list_evidence(
        cls,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        control_id: Optional[uuid.UUID] = None,
    ) -> List[Evidence]:
        stmt = select(Evidence).where(Evidence.tenant_id == tenant_id)
        if control_id:
            stmt = stmt.where(Evidence.control_id == control_id)
        stmt = stmt.order_by(Evidence.uploaded_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def get_evidence(
        cls,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        evidence_id: uuid.UUID,
    ) -> Evidence:
        stmt = select(Evidence).where(
            Evidence.evidence_id == evidence_id,
            Evidence.tenant_id == tenant_id
        )
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")
        return record

