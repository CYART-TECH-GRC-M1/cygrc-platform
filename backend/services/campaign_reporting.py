import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.campaign import (
    RedTeamCampaign,
    RedTeamExecutionJob,
    AtomicTestExecution,
    DetectionVerificationRecord,
    CampaignReport,
)
from backend.services.mitre_attack import MitreAttackService


class CampaignReportingService:
    """
    Generates and persists comprehensive post-campaign reports.
    Computes verified dynamic coverage metrics, identifies detection gaps,
    and links findings to SOC detection engineering remediation backlog.
    """

    @classmethod
    async def generate_final_report(
        cls,
        db: AsyncSession,
        tenant_id: str,
        campaign_id: str,
        operator_id: Optional[str] = None,
    ) -> CampaignReport:
        """
        Generates full post-campaign evaluation report and persists to DB.
        """
        stmt = select(RedTeamCampaign).where(
            RedTeamCampaign.campaign_id == campaign_id,
            RedTeamCampaign.tenant_id == tenant_id,
        )
        res = await db.execute(stmt)
        campaign = res.scalar_one_or_none()
        if not campaign:
            raise ValueError(f"Campaign '{campaign_id}' not found")

        # 1. Fetch execution jobs and atomic executions
        jobs_stmt = select(RedTeamExecutionJob).where(
            RedTeamExecutionJob.campaign_id == campaign_id,
            RedTeamExecutionJob.tenant_id == tenant_id,
        )
        jobs_res = await db.execute(jobs_stmt)
        jobs = jobs_res.scalars().all()

        atomic_stmt = select(AtomicTestExecution).where(
            AtomicTestExecution.campaign_id == campaign_id,
            AtomicTestExecution.tenant_id == tenant_id,
        )
        atomic_res = await db.execute(atomic_stmt)
        atomic_tests = atomic_res.scalars().all()

        # 2. Fetch detection verification records
        verif_stmt = select(DetectionVerificationRecord).where(
            DetectionVerificationRecord.campaign_id == campaign_id,
            DetectionVerificationRecord.tenant_id == tenant_id,
        )
        verif_res = await db.execute(verif_stmt)
        verifications = verif_res.scalars().all()

        # 3. Categorize actions
        planned_set = set(t.upper() for t in (campaign.techniques_tested or []))
        if campaign.technique_catalogue:
            for item in campaign.technique_catalogue:
                if isinstance(item, str):
                    planned_set.add(item.upper())
                elif isinstance(item, dict) and "id" in item:
                    planned_set.add(item["id"].upper())

        executed_set = set()
        failed_set = set()
        inconclusive_set = set()

        for j in jobs:
            tech_ids = [tid.strip().upper() for tid in (j.technique_id or "").split(",") if tid.strip()]
            for tid in tech_ids:
                if j.status in ["EXECUTED", "SUCCESS"]:
                    executed_set.add(tid)
                elif j.status in ["FAILED"]:
                    failed_set.add(tid)
                elif j.status in ["TIMEOUT", "CANCELLED"]:
                    inconclusive_set.add(tid)

        for a in atomic_tests:
            tid = a.technique_id.strip().upper()
            if a.status == "SUCCESS":
                executed_set.add(tid)
            elif a.status == "FAILED":
                failed_set.add(tid)
            elif a.status in ["TIMEOUT", "CANCELLED"]:
                inconclusive_set.add(tid)

        detected_set = set()
        for v in verifications:
            tid = v.technique_id.strip().upper()
            if v.status in ["DETECTED", "MANUALLY_VERIFIED"]:
                detected_set.add(tid)

        # Dynamic coverage calculations
        metrics = MitreAttackService.calculate_campaign_coverage(
            planned_techniques=list(planned_set),
            executed_techniques=list(executed_set),
            detected_techniques=list(detected_set),
            failed_techniques=list(failed_set),
        )

        gaps_set = executed_set - detected_set

        # 4. Generate remediation backlog
        remediation_backlog = []
        for gap_tid in sorted(list(gaps_set)):
            tech_info = MitreAttackService.get_technique_details(gap_tid) or {}
            remediation_backlog.append({
                "backlog_id": f"REM-{gap_tid}-{uuid.uuid4().hex[:6].upper()}",
                "technique_id": gap_tid,
                "technique_name": tech_info.get("technique_name", "Unknown Technique"),
                "tactic_id": tech_info.get("tactic_id", "Unknown"),
                "tactic_name": tech_info.get("tactic_name", "Unknown"),
                "issue": f"Adversary technique {gap_tid} executed without SOC alert detection.",
                "priority": "HIGH" if tech_info.get("tactic_id") in ["TA0001", "TA0006", "TA0040"] else "MEDIUM",
                "recommended_action": f"Author and deploy Sigma/Wazuh detection rule for {tech_info.get('technique_name', gap_tid)}.",
                "linked_soc_phase": "DETECTION_ANALYSIS",
            })

        # 5. Build Executive Summary
        exec_summary = (
            f"Red Team Campaign '{campaign.name}' Evaluation Report.\n"
            f"Objective: {campaign.objective or campaign.description or 'Adversary simulation and purple team detection verification'}.\n"
            f"Framework Version: {MitreAttackService.VERSION}.\n"
            f"Results Summary: {len(planned_set)} Planned Techniques, {len(executed_set)} Executed, "
            f"{len(detected_set)} Detected ({metrics['detection_coverage_pct']}%), "
            f"{len(gaps_set)} Detection Gaps Identified ({metrics['gap_percentage']}%).\n"
            f"Total Execution Jobs: {len(jobs) + len(atomic_tests)}. Inconclusive/Timed out: {len(inconclusive_set)}.\n"
            f"Status: Post-exercise findings transferred to SOC Detection Engineering Backlog."
        )

        report = CampaignReport(
            tenant_id=tenant_id,
            campaign_id=campaign_id,
            title=f"Final Assessment Report: {campaign.name}",
            executive_summary=exec_summary,
            attack_matrix_version=MitreAttackService.VERSION,
            total_planned=len(planned_set),
            total_attempted=len(executed_set) + len(failed_set),
            total_executed=len(executed_set),
            total_failed=len(failed_set),
            total_detected=len(detected_set),
            detection_gaps=len(gaps_set),
            inconclusive=len(inconclusive_set),
            planned_coverage_pct=metrics["planned_coverage_pct"],
            execution_coverage_pct=metrics["execution_coverage_pct"],
            detection_coverage_pct=metrics["detection_coverage_pct"],
            gap_percentage=metrics["gap_percentage"],
            remediation_backlog=remediation_backlog,
        )
        db.add(report)

        # Update campaign state
        campaign.status = "COMPLETED"
        campaign.coverage_score = f"{metrics['detection_coverage_pct']}%"
        campaign.execution_summary = {
            "total_planned": len(planned_set),
            "total_executed": len(executed_set),
            "total_detected": len(detected_set),
            "detection_gaps": len(gaps_set),
            "detection_coverage_pct": metrics["detection_coverage_pct"],
            "gap_percentage": metrics["gap_percentage"],
            "completed_at": datetime.utcnow().isoformat(),
        }

        await db.commit()
        await db.refresh(report)
        return report

    @classmethod
    async def get_latest_report(
        cls,
        db: AsyncSession,
        tenant_id: str,
        campaign_id: str,
    ) -> Optional[CampaignReport]:
        stmt = select(CampaignReport).where(
            CampaignReport.campaign_id == campaign_id,
            CampaignReport.tenant_id == tenant_id,
        ).order_by(CampaignReport.created_at.desc())
        res = await db.execute(stmt)
        return res.scalar_one_or_none()
