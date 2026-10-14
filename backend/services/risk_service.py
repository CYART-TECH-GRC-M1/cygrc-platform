import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from backend.models.risk import Risk, RiskAssessment, RiskTreatment, RiskTreatmentStatus
from backend.models.tenant import TenantStatus
from backend.models.control import Control
from backend.schemas.risk import RiskCreate, RiskUpdate, RiskAssessmentCreate, RiskTreatmentCreate


class RiskService:
    @staticmethod
    def calculate_score(likelihood: Optional[int], impact: Optional[int]) -> Optional[int]:
        if likelihood is not None and impact is not None:
            return likelihood * impact
        return None

    @classmethod
    async def create_risk(
        cls,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        payload: RiskCreate,
        created_by: Optional[uuid.UUID] = None,
    ) -> Risk:
        if payload.control_id:
            ctrl = await db.get(Control, payload.control_id)
            if not ctrl:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Control {payload.control_id} does not exist"
                )

        score = cls.calculate_score(payload.likelihood, payload.impact)
        status_enum = TenantStatus(payload.status) if payload.status in TenantStatus.__members__ else TenantStatus.ACTIVE

        risk = Risk(
            tenant_id=tenant_id,
            control_id=payload.control_id,
            title=payload.title,
            description=payload.description,
            likelihood=payload.likelihood,
            impact=payload.impact,
            risk_score=score,
            status=status_enum,
            created_by=created_by,
        )
        db.add(risk)
        await db.commit()
        await db.refresh(risk)
        return risk

    @classmethod
    async def list_risks(
        cls,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        control_id: Optional[uuid.UUID] = None,
    ) -> List[Risk]:
        stmt = select(Risk).where(Risk.tenant_id == tenant_id)
        if control_id:
            stmt = stmt.where(Risk.control_id == control_id)
        stmt = stmt.order_by(Risk.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def get_risk(cls, db: AsyncSession, tenant_id: uuid.UUID, risk_id: uuid.UUID) -> Risk:
        stmt = select(Risk).where(Risk.risk_id == risk_id, Risk.tenant_id == tenant_id)
        result = await db.execute(stmt)
        risk = result.scalar_one_or_none()
        if not risk:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk not found")
        return risk

    @classmethod
    async def update_risk(
        cls,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        risk_id: uuid.UUID,
        payload: RiskUpdate,
    ) -> Risk:
        risk = await cls.get_risk(db, tenant_id, risk_id)
        update_data = payload.dict(exclude_unset=True)

        if "control_id" in update_data and update_data["control_id"]:
            ctrl = await db.get(Control, update_data["control_id"])
            if not ctrl:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Control {update_data['control_id']} does not exist"
                )

        for key, value in update_data.items():
            if key == "status" and value:
                setattr(risk, key, TenantStatus(value) if value in TenantStatus.__members__ else TenantStatus.ACTIVE)
            else:
                setattr(risk, key, value)

        risk.risk_score = cls.calculate_score(risk.likelihood, risk.impact)
        await db.commit()
        await db.refresh(risk)
        return risk

    @classmethod
    async def delete_risk(cls, db: AsyncSession, tenant_id: uuid.UUID, risk_id: uuid.UUID) -> None:
        risk = await cls.get_risk(db, tenant_id, risk_id)
        await db.delete(risk)
        await db.commit()

    @classmethod
    async def add_assessment(
        cls,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        risk_id: uuid.UUID,
        payload: RiskAssessmentCreate,
        assessor_id: uuid.UUID,
    ) -> RiskAssessment:
        risk = await cls.get_risk(db, tenant_id, risk_id)
        score = payload.likelihood * payload.impact

        assessment = RiskAssessment(
            risk_id=risk.risk_id,
            assessor_id=assessor_id,
            likelihood=payload.likelihood,
            impact=payload.impact,
            risk_score=score,
            comments=payload.comments,
        )
        # Update parent risk score with latest assessment
        risk.likelihood = payload.likelihood
        risk.impact = payload.impact
        risk.risk_score = score

        db.add(assessment)
        await db.commit()
        await db.refresh(assessment)
        return assessment

    @classmethod
    async def add_treatment(
        cls,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        risk_id: uuid.UUID,
        payload: RiskTreatmentCreate,
    ) -> RiskTreatment:
        risk = await cls.get_risk(db, tenant_id, risk_id)
        treatment_status = (
            RiskTreatmentStatus(payload.status)
            if payload.status in RiskTreatmentStatus.__members__
            else RiskTreatmentStatus.OPEN
        )

        treatment = RiskTreatment(
            risk_id=risk.risk_id,
            owner_id=payload.owner_id,
            treatment_plan=payload.treatment_plan,
            target_date=payload.target_date,
            status=treatment_status,
        )
        db.add(treatment)
        await db.commit()
        await db.refresh(treatment)
        return treatment

