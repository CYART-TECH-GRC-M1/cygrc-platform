"""Durable Scan Scheduler and Execution Engine for VAPT.

Features:
- Database persistence for schedules and scan jobs.
- Target authorization scope validation.
- Concurrency control and deduplication of running jobs.
- Prevention of duplicate background runs.
- Full scan history and audit trail.
"""
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.audit import record_audit_log
from backend.models.asset import Asset
from backend.models.scan_schedule import ScanSchedule, ScanJob
from backend.models.vulnerability_finding import VulnerabilityFinding
from backend.services.scanner_adapters import (
    NmapScannerAdapter,
    OWASPZapAdapter,
    OpenVASScannerAdapter,
    TargetScopeValidator,
)

logger = logging.getLogger(__name__)


class ScanSchedulerService:
    DEFAULT_CONCURRENCY_LIMIT = 3

    FREQUENCY_INTERVALS = {
        "ONCE": timedelta(days=3650),
        "HOURLY": timedelta(hours=1),
        "DAILY": timedelta(days=1),
        "WEEKLY": timedelta(weeks=1),
        "MONTHLY": timedelta(days=30),
    }

    @classmethod
    async def create_scan_schedule(
        cls,
        tenant_id: str,
        target: Optional[str] = None,
        scan_type: str = "NETWORK_NMAP",
        frequency: str = "DAILY",
        asset_id: Optional[str] = None,
        asset_name: Optional[str] = None,
        concurrency_limit: int = 2,
        db: Optional[AsyncSession] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Creates a durable scan schedule record in database."""
        effective_target = target or asset_name or asset_id or "127.0.0.1"

        # 1. Scope validation
        is_valid, err, normalized_target = TargetScopeValidator.validate_target(effective_target)
        if not is_valid:
            raise ValueError(f"Scan target validation rejected: {err}")

        now = datetime.now(timezone.utc)
        interval = cls.FREQUENCY_INTERVALS.get(frequency.upper(), timedelta(days=1))
        next_run = now + (interval if frequency.upper() != "ONCE" else timedelta(minutes=5))

        schedule = ScanSchedule(
            tenant_id=tenant_id,
            asset_id=asset_id,
            target=normalized_target,
            scan_type=scan_type.upper(),
            frequency=frequency.upper(),
            status="ACTIVE",
            concurrency_limit=concurrency_limit or cls.DEFAULT_CONCURRENCY_LIMIT,
            next_run_at=next_run,
        )

        if db is not None:
            db.add(schedule)
            await db.commit()
            await db.refresh(schedule)

            await record_audit_log(
                action="scan_schedule:create",
                tenant_id=tenant_id,
                resource_type="scan_schedule",
                resource_id=schedule.schedule_id,
                details={"target": normalized_target, "scan_type": scan_type, "frequency": frequency},
                db=db,
            )

        sched_data = {
            "schedule_id": schedule.schedule_id,
            "tenant_id": schedule.tenant_id,
            "asset_id": schedule.asset_id,
            "target": schedule.target,
            "scan_type": schedule.scan_type,
            "frequency": schedule.frequency,
            "status": schedule.status,
            "schedule_status": schedule.status,
            "next_run_at": schedule.next_run_at.isoformat(),
            "created_at": schedule.created_at.isoformat() if schedule.created_at else now.isoformat(),
        }

        return {
            **sched_data,
            "status": "SUCCESS",
            "schedule_status": schedule.status,
            "schedule": sched_data,
        }

    @classmethod
    async def update_schedule_status(
        cls,
        schedule_id: str,
        tenant_id: str,
        new_status: str,
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """Pauses, resumes, or cancels an existing scan schedule."""
        valid_statuses = {"ACTIVE", "PAUSED", "CANCELLED", "COMPLETED"}
        target_status = new_status.upper()
        if target_status not in valid_statuses:
            raise ValueError(f"Invalid schedule status '{new_status}'. Allowed: {valid_statuses}")

        stmt = select(ScanSchedule).where(
            ScanSchedule.schedule_id == schedule_id,
            ScanSchedule.tenant_id == tenant_id
        )
        res = await db.execute(stmt)
        sched = res.scalar_one_or_none()
        if not sched:
            raise LookupError(f"Schedule '{schedule_id}' not found.")

        old_status = sched.status
        sched.status = target_status
        sched.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(sched)

        await record_audit_log(
            action="scan_schedule:update_status",
            tenant_id=tenant_id,
            resource_type="scan_schedule",
            resource_id=schedule_id,
            details={"previous_status": old_status, "new_status": target_status},
            db=db,
        )

        return {
            "schedule_id": sched.schedule_id,
            "status": sched.status,
            "previous_status": old_status,
            "updated_at": sched.updated_at.isoformat(),
        }

    @classmethod
    async def trigger_scan_job(
        cls,
        tenant_id: str,
        target: str,
        scan_type: str = "NETWORK_NMAP",
        schedule_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ) -> Dict[str, Any]:
        """
        Launches an authorized scan job.
        Enforces target authorization, concurrency limits, and running job deduplication.
        """
        is_valid, err, normalized_target = TargetScopeValidator.validate_target(target)
        if not is_valid:
            return {
                "success": False,
                "status": "SCOPE_REJECTED",
                "error": f"Target scope authorization rejected: {err}",
            }

        now = datetime.now(timezone.utc)

        # Concurrency & Deduplication Checks (if DB available)
        if db is not None:
            # 1. Prevent overlapping jobs on exact same target
            dup_stmt = select(ScanJob).where(
                ScanJob.tenant_id == tenant_id,
                ScanJob.target == normalized_target,
                ScanJob.status == "RUNNING",
            )
            dup_res = await db.execute(dup_stmt)
            if dup_res.scalar_one_or_none():
                return {
                    "success": False,
                    "status": "CONCURRENT_JOB_RUNNING",
                    "error": f"A scan job is already actively running for target '{normalized_target}'. Duplicate run prevented.",
                }

            # 2. Concurrency limit check
            active_count_stmt = select(func.count(ScanJob.job_id)).where(
                ScanJob.tenant_id == tenant_id,
                ScanJob.status == "RUNNING",
            )
            count_res = await db.execute(active_count_stmt)
            active_running = count_res.scalar() or 0
            if active_running >= cls.DEFAULT_CONCURRENCY_LIMIT:
                return {
                    "success": False,
                    "status": "CONCURRENCY_LIMIT_EXCEEDED",
                    "error": f"Maximum concurrent scan limit ({cls.DEFAULT_CONCURRENCY_LIMIT}) reached for this tenant.",
                }

        # Create Job Record
        job = ScanJob(
            schedule_id=schedule_id,
            tenant_id=tenant_id,
            asset_id=asset_id,
            target=normalized_target,
            scan_type=scan_type.upper(),
            scanner_tool="NMAP" if "NMAP" in scan_type.upper() or "PORT" in scan_type.upper() else ("ZAP" if "ZAP" in scan_type.upper() or "WEB" in scan_type.upper() else "OPENVAS"),
            status="RUNNING",
            started_at=now,
        )

        if db is not None:
            db.add(job)
            await db.commit()
            await db.refresh(job)

        # Dispatch scan through appropriate scanner adapter
        discovered_assets = []
        findings_count = 0
        error_msg = None

        if "ZAP" in job.scan_type or "WEB" in job.scan_type:
            scan_res = await OWASPZapAdapter.run_scan_or_fixture(normalized_target)
            if scan_res.get("success"):
                job.status = "COMPLETED"
                alerts = scan_res.get("alerts", [])
                findings_count = len(alerts)
                job.summary = f"OWASP ZAP scan discovered {findings_count} web security alerts."
                job.raw_output = json.dumps(alerts)
            else:
                job.status = "FAILED"
                error_msg = scan_res.get("error", "ZAP scan failed.")
        elif "OPENVAS" in job.scan_type or "VULN" in job.scan_type:
            scan_res = OpenVASScannerAdapter.run_scan_or_fixture(normalized_target)
            if scan_res.get("success"):
                job.status = "COMPLETED"
                vulns = scan_res.get("findings", [])
                findings_count = len(vulns)
                job.summary = f"OpenVAS vulnerability scan reported {findings_count} CVE findings."
                job.raw_output = json.dumps(vulns)
            else:
                job.status = "FAILED"
                error_msg = scan_res.get("error", "OpenVAS scan failed.")
        else:
            # Default: Network Nmap scan
            scan_res = NmapScannerAdapter.execute_scan(normalized_target)
            if scan_res.get("success"):
                job.status = "COMPLETED"
                hosts = scan_res.get("hosts", [])
                discovered_assets = hosts
                job.summary = f"Nmap discovery completed: {len(hosts)} active hosts identified."
                job.raw_output = scan_res.get("raw_output", "")
            else:
                job.status = "FAILED"
                error_msg = scan_res.get("error", "Nmap scan failed.")

        job.completed_at = datetime.now(timezone.utc)
        job.findings_count = findings_count
        job.error_message = error_msg

        if db is not None:
            # Reconcile discovered hosts into assets table
            from backend.services.asset_discovery import AssetDiscoveryService
            if discovered_assets:
                await AssetDiscoveryService.process_nmap_discovery(
                    {"hosts": discovered_assets},
                    tenant_id=tenant_id,
                    db=db,
                )

            # Persist vulnerability findings for web and vuln scans
            if job.status == "COMPLETED" and (scan_res.get("alerts") or scan_res.get("findings")):
                from backend.services.vulnerability_prioritization import VulnerabilityPrioritizationService
                effective_asset_id = job.asset_id
                asset_crit = "MEDIUM"
                if effective_asset_id:
                    a_stmt = select(Asset).where(Asset.asset_id == effective_asset_id)
                    a_res = await db.execute(a_stmt)
                    target_asset = a_res.scalar_one_or_none()
                    if target_asset:
                        asset_crit = target_asset.criticality
                else:
                    a_stmt = select(Asset).where(Asset.tenant_id == tenant_id, Asset.name == job.target)
                    a_res = await db.execute(a_stmt)
                    target_asset = a_res.scalar_one_or_none()
                    if not target_asset:
                        target_asset = Asset(
                            tenant_id=tenant_id,
                            name=job.target,
                            asset_type="WEB_APP" if "ZAP" in job.scanner_tool else "SERVER",
                            status="ACTIVE",
                            criticality="HIGH",
                        )
                        db.add(target_asset)
                        await db.flush()
                    effective_asset_id = target_asset.asset_id
                    asset_crit = target_asset.criticality

                if "alerts" in scan_res:
                    for alert in scan_res["alerts"]:
                        cwe = f"CWE-{alert.get('cweid')}" if alert.get("cweid") else None
                        sev = alert.get("risk", "MEDIUM").upper()
                        base_cvss = 7.5 if sev == "HIGH" else 5.0
                        p_res = VulnerabilityPrioritizationService.calculate_priority_score(
                            cvss_score=base_cvss,
                            is_cisa_kev=False,
                            asset_criticality=asset_crit,
                        )
                        vf = VulnerabilityFinding(
                            tenant_id=tenant_id,
                            asset_id=effective_asset_id,
                            scan_job_id=job.job_id,
                            cve_id=cwe,
                            title=alert.get("alert", "Web Vulnerability"),
                            severity=sev,
                            cvss_score=base_cvss,
                            priority_score=p_res["priority_score"],
                            priority_level=p_res["priority_level"],
                            scanner_source="ZAP",
                            evidence=alert.get("evidence"),
                            remediation=alert.get("solution"),
                            status="OPEN",
                        )
                        db.add(vf)

                if "findings" in scan_res:
                    for vuln in scan_res["findings"]:
                        score = vuln.get("severity", 5.0)
                        p_res = VulnerabilityPrioritizationService.calculate_priority_score(
                            cvss_score=score,
                            is_cisa_kev=False,
                            asset_criticality=asset_crit,
                        )
                        vf = VulnerabilityFinding(
                            tenant_id=tenant_id,
                            asset_id=effective_asset_id,
                            scan_job_id=job.job_id,
                            cve_id=vuln.get("cve"),
                            title=vuln.get("name", "Vulnerability"),
                            severity="HIGH" if score >= 7.0 else "MEDIUM",
                            cvss_score=score,
                            priority_score=p_res["priority_score"],
                            priority_level=p_res["priority_level"],
                            scanner_source="OPENVAS",
                            evidence=vuln.get("description"),
                            remediation=vuln.get("solution"),
                            status="OPEN",
                        )
                        db.add(vf)

            await db.commit()
            await db.refresh(job)

            await record_audit_log(
                action="scan_job:execute",
                tenant_id=tenant_id,
                resource_type="scan_job",
                resource_id=job.job_id,
                result="SUCCESS" if job.status == "COMPLETED" else "FAILURE",
                details={
                    "target": normalized_target,
                    "scan_type": job.scan_type,
                    "findings_count": findings_count,
                    "status": job.status,
                },
                db=db,
            )

        return {
            "success": job.status == "COMPLETED",
            "job_id": job.job_id,
            "tenant_id": job.tenant_id,
            "target": job.target,
            "scan_type": job.scan_type,
            "scanner_tool": job.scanner_tool,
            "status": job.status,
            "findings_count": job.findings_count,
            "summary": job.summary,
            "error_message": job.error_message,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        }

    @classmethod
    async def list_jobs(
        cls,
        tenant_id: str,
        db: AsyncSession,
        schedule_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[ScanJob]:
        stmt = select(ScanJob).where(ScanJob.tenant_id == tenant_id)
        if schedule_id:
            stmt = stmt.where(ScanJob.schedule_id == schedule_id)
        stmt = stmt.order_by(ScanJob.created_at.desc()).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())
