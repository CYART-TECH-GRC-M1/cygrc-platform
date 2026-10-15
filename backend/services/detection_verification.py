from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from backend.models.alert import Alert
from backend.models.campaign import DetectionVerificationRecord


class DetectionVerificationService:
    """
    Correlates Red Team executions with actual SOC alerts and telemetry.
    Records detection rules fired, evidence references, manual analyst verifications,
    and identifies detection gaps.
    """

    @classmethod
    async def correlate_execution(
        cls,
        db: AsyncSession,
        tenant_id: str,
        execution_id: str,
        technique_id: str,
        campaign_id: Optional[str] = None,
        target_asset_id: Optional[str] = None,
        execution_time: Optional[datetime] = None,
    ) -> DetectionVerificationRecord:
        """
        Correlates a test execution against stored SOC alerts in the database.
        Checks technique ID tags, descriptions, asset IDs, and creation timestamps.
        """
        tid = technique_id.strip().upper()
        window_start = (execution_time or datetime.utcnow()) - timedelta(minutes=15)

        # Query alerts belonging to tenant
        stmt = select(Alert).where(
            Alert.tenant_id == tenant_id,
            Alert.created_at >= window_start,
        )
        res = await db.execute(stmt)
        recent_alerts = res.scalars().all()

        matched_alerts: List[Alert] = []
        rules_fired: List[str] = []

        for alert in recent_alerts:
            title_upper = (alert.title or "").upper()
            desc_upper = (alert.description or "").upper()

            # Check if alert references the MITRE technique ID or target
            technique_match = tid in title_upper or tid in desc_upper
            asset_match = target_asset_id and (target_asset_id in title_upper or target_asset_id in desc_upper)

            if technique_match or (asset_match and "TEST" in title_upper):
                matched_alerts.append(alert)
                rule_name = f"{alert.source}: {alert.title}"
                if rule_name not in rules_fired:
                    rules_fired.append(rule_name)

        # Fallback check across all tenant alerts if no recent ones matched
        if not matched_alerts:
            fallback_stmt = select(Alert).where(
                Alert.tenant_id == tenant_id,
                or_(
                    Alert.title.ilike(f"%{tid}%"),
                    Alert.description.ilike(f"%{tid}%"),
                )
            ).order_by(Alert.created_at.desc()).limit(5)
            f_res = await db.execute(fallback_stmt)
            for alert in f_res.scalars().all():
                matched_alerts.append(alert)
                rule_name = f"{alert.source}: {alert.title}"
                if rule_name not in rules_fired:
                    rules_fired.append(rule_name)

        status = "DETECTED" if len(matched_alerts) > 0 else "GAP"

        matched_ids = [a.alert_id for a in matched_alerts]
        evidence = {
            "matched_alerts_count": len(matched_alerts),
            "matched_severities": [a.severity for a in matched_alerts],
            "correlation_timestamp": datetime.utcnow().isoformat(),
            "technique_id": tid,
            "target_asset_id": target_asset_id,
        }

        verification = DetectionVerificationRecord(
            tenant_id=tenant_id,
            campaign_id=campaign_id,
            execution_id=execution_id,
            technique_id=tid,
            status=status,
            matched_alert_ids=matched_ids,
            detection_rules_fired=rules_fired,
            evidence_references=evidence,
            notes=f"Correlation completed. Found {len(matched_alerts)} matching alerts." if status == "DETECTED" else "No matching alerts found within detection correlation window. Detection gap recorded.",
        )
        db.add(verification)
        await db.commit()
        await db.refresh(verification)
        return verification

    @classmethod
    async def manually_verify(
        cls,
        db: AsyncSession,
        tenant_id: str,
        verification_id: str,
        analyst_name: str,
        notes: str,
        status: str = "MANUALLY_VERIFIED",
    ) -> DetectionVerificationRecord:
        """
        Analyst manual sign-off and verification update.
        """
        stmt = select(DetectionVerificationRecord).where(
            DetectionVerificationRecord.verification_id == verification_id,
            DetectionVerificationRecord.tenant_id == tenant_id,
        )
        res = await db.execute(stmt)
        record = res.scalar_one_or_none()
        if not record:
            raise ValueError(f"Verification record '{verification_id}' not found")

        record.status = status
        record.verified_by = analyst_name
        record.verified_at = datetime.utcnow()
        record.notes = (record.notes or "") + f"\n[Analyst Review by {analyst_name}]: {notes}"

        await db.commit()
        await db.refresh(record)
        return record

    @classmethod
    async def get_detection_gaps(
        cls,
        db: AsyncSession,
        tenant_id: str,
        campaign_id: Optional[str] = None,
    ) -> List[DetectionVerificationRecord]:
        """
        Queries all verified detection gaps for the tenant or campaign.
        """
        stmt = select(DetectionVerificationRecord).where(
            DetectionVerificationRecord.tenant_id == tenant_id,
            DetectionVerificationRecord.status == "GAP",
        )
        if campaign_id:
            stmt = stmt.where(DetectionVerificationRecord.campaign_id == campaign_id)

        res = await db.execute(stmt.order_by(DetectionVerificationRecord.created_at.desc()))
        return res.scalars().all()
