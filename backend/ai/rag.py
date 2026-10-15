import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.permissions import Permission, has_permission
from backend.ai.guardrails import PromptInjectionDetector
from backend.models.alert import Alert
from backend.models.incident_case import IncidentCase
from backend.models.asset import Asset
from backend.models.vulnerability_finding import VulnerabilityFinding
from backend.models.cve_finding import CVEFinding
from backend.models.stix_object import StixObject
from backend.models.chain_of_custody import ChainOfCustody

logger = logging.getLogger("cygrc.ai.rag")


@dataclass
class AuthorizedSourceRecord:
    record_id: str
    record_type: str  # alert, case, finding, cve, asset, stix, custody
    title: str
    snippet: str
    timestamp: str
    tenant_id: str


class AuthorizedRetriever:
    """
    Authorized Multi-Source Retrieval Engine.
    Enforces strict tenant isolation, role-based resource access,
    freshness ordering, and context size limits.
    Wraps untrusted records to protect against indirect prompt injections.
    """

    MAX_RECORDS_PER_TYPE = 8
    MAX_TOTAL_CONTEXT_CHARS = 14000

    @classmethod
    async def retrieve_records(
        cls,
        db: AsyncSession,
        tenant_id: str,
        user_roles: List[str],
        query_text: Optional[str] = None,
        specific_alert_ids: Optional[List[str]] = None,
        specific_case_ids: Optional[List[str]] = None,
        specific_finding_ids: Optional[List[str]] = None,
        specific_asset_ids: Optional[List[str]] = None,
        specific_cve_ids: Optional[List[str]] = None,
        specific_indicators: Optional[List[str]] = None,
    ) -> Tuple[str, Dict[str, AuthorizedSourceRecord]]:
        """
        Executes authorized retrieval across all relevant persisted tables.
        Returns: (formatted_untrusted_context_string, authorized_records_map)
        """
        authorized_records: Dict[str, AuthorizedSourceRecord] = {}
        context_blocks: List[str] = []

        # 1. ALERTS (requires alert:view permission)
        if has_permission(user_roles, Permission.ALERT_VIEW):
            alerts = await cls._retrieve_alerts(db, tenant_id, specific_alert_ids, query_text)
            for a in alerts:
                rec = AuthorizedSourceRecord(
                    record_id=a.alert_id,
                    record_type="ALERT",
                    title=a.title,
                    snippet=f"Source: {a.source} | Severity: {a.severity} | Status: {a.status} | {a.description or ''}",
                    timestamp=a.created_at.isoformat() if a.created_at else "",
                    tenant_id=tenant_id,
                )
                authorized_records[a.alert_id] = rec
                context_blocks.append(cls._format_untrusted_block(rec))

        # 2. INCIDENT CASES (requires case:view permission)
        if has_permission(user_roles, Permission.CASE_VIEW):
            cases = await cls._retrieve_cases(db, tenant_id, specific_case_ids, query_text)
            for c in cases:
                rec = AuthorizedSourceRecord(
                    record_id=c.case_id,
                    record_type="CASE",
                    title=f"{c.case_number}: {c.title}",
                    snippet=f"Phase: {c.nist_phase} | Severity: {c.severity} | Status: {c.status} | {c.summary or ''}",
                    timestamp=c.created_at.isoformat() if c.created_at else "",
                    tenant_id=tenant_id,
                )
                authorized_records[c.case_id] = rec
                authorized_records[c.case_number] = rec
                context_blocks.append(cls._format_untrusted_block(rec))

        # 3. ASSETS (requires asset:view permission)
        if has_permission(user_roles, Permission.ASSET_VIEW):
            assets = await cls._retrieve_assets(db, tenant_id, specific_asset_ids, query_text)
            for ast in assets:
                rec = AuthorizedSourceRecord(
                    record_id=ast.asset_id,
                    record_type="ASSET",
                    title=ast.name,
                    snippet=f"Type: {ast.asset_type} | IP: {ast.ip_address} | Host: {ast.hostname} | Exposure: {ast.exposure} | Criticality: {ast.criticality}",
                    timestamp=ast.created_at.isoformat() if ast.created_at else "",
                    tenant_id=tenant_id,
                )
                authorized_records[ast.asset_id] = rec
                context_blocks.append(cls._format_untrusted_block(rec))

        # 4. VULNERABILITY FINDINGS (requires asset:view or vapt permissions)
        if has_permission(user_roles, Permission.ASSET_VIEW):
            findings = await cls._retrieve_findings(db, tenant_id, specific_finding_ids, specific_cve_ids)
            for f in findings:
                rec = AuthorizedSourceRecord(
                    record_id=f.finding_id,
                    record_type="FINDING",
                    title=f.title,
                    snippet=f"Asset: {f.asset_id} | CVE: {f.cve_id} | Severity: {f.severity} | Score: {f.priority_score} | Remediation: {f.remediation or ''}",
                    timestamp=f.created_at.isoformat() if f.created_at else "",
                    tenant_id=tenant_id,
                )
                authorized_records[f.finding_id] = rec
                if f.cve_id:
                    authorized_records[f.cve_id] = rec
                context_blocks.append(cls._format_untrusted_block(rec))

        # 5. GLOBAL CVEs
        if specific_cve_ids:
            cves = await cls._retrieve_cves(db, specific_cve_ids)
            for c in cves:
                rec = AuthorizedSourceRecord(
                    record_id=c.cve_id,
                    record_type="CVE",
                    title=c.cve_id,
                    snippet=f"CVSS: {c.cvss_score} | KEV: {c.cisa_kev} | Product: {c.affected_product} | Summary: {c.summary or ''}",
                    timestamp=c.published_date.isoformat() if c.published_date else "",
                    tenant_id=tenant_id,
                )
                authorized_records[c.cve_id] = rec
                context_blocks.append(cls._format_untrusted_block(rec))

        # 6. THREAT INTEL / STIX (requires intel:view permission)
        if has_permission(user_roles, Permission.INTEL_VIEW):
            stix_objs = await cls._retrieve_stix(db, tenant_id, specific_indicators, query_text)
            for s in stix_objs:
                rec = AuthorizedSourceRecord(
                    record_id=s.stix_id,
                    record_type="STIX",
                    title=s.name or s.stix_id,
                    snippet=f"Type: {s.type} | Pattern: {s.pattern or ''} | Confidence: {s.confidence} | Description: {s.description or ''}",
                    timestamp=s.created_at.isoformat() if s.created_at else "",
                    tenant_id=tenant_id,
                )
                authorized_records[s.stix_id] = rec
                context_blocks.append(cls._format_untrusted_block(rec))

        # 7. CHAIN OF CUSTODY (requires custody:view permission)
        if has_permission(user_roles, Permission.CUSTODY_VIEW):
            custody = await cls._retrieve_custody(db, tenant_id)
            for cy in custody:
                rec = AuthorizedSourceRecord(
                    record_id=cy.custody_id,
                    record_type="CUSTODY",
                    title=f"Evidence {cy.evidence_id} - {cy.action}",
                    snippet=f"Custodian: {cy.custodian_name} | SHA256: {cy.hash_sha256} | Desc: {cy.item_description}",
                    timestamp=cy.timestamp.isoformat() if cy.timestamp else "",
                    tenant_id=tenant_id,
                )
                authorized_records[cy.custody_id] = rec
                authorized_records[cy.evidence_id] = rec
                context_blocks.append(cls._format_untrusted_block(rec))

        # Enforce context size limits to protect against token exhaustion
        combined_context = "\n".join(context_blocks)
        if len(combined_context) > cls.MAX_TOTAL_CONTEXT_CHARS:
            combined_context = combined_context[: cls.MAX_TOTAL_CONTEXT_CHARS] + "\n[CONTEXT_TRUNCATED_DUE_TO_SIZE_LIMIT]"

        return combined_context, authorized_records

    @classmethod
    def _format_untrusted_block(cls, rec: AuthorizedSourceRecord) -> str:
        """Wraps untrusted record text in strict delimiter tags with neutralized injection keywords."""
        sanitized_snippet = PromptInjectionDetector.sanitize_untrusted_input(rec.snippet)
        sanitized_title = PromptInjectionDetector.sanitize_untrusted_input(rec.title)
        return (
            f"<untrusted_record type=\"{rec.record_type}\" id=\"{rec.record_id}\" "
            f"timestamp=\"{rec.timestamp}\">\n"
            f"Title: {sanitized_title}\n"
            f"Details: {sanitized_snippet}\n"
            f"</untrusted_record>"
        )

    @classmethod
    async def _retrieve_alerts(
        cls, db: AsyncSession, tenant_id: str, specific_ids: Optional[List[str]], query: Optional[str]
    ) -> List[Alert]:
        stmt = select(Alert).where(
            or_(Alert.tenant_id == tenant_id, Alert.tenant_id.is_(None))
        )
        if specific_ids:
            stmt = stmt.where(Alert.alert_id.in_(specific_ids))
        stmt = stmt.order_by(Alert.created_at.desc()).limit(cls.MAX_RECORDS_PER_TYPE)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    async def _retrieve_cases(
        cls, db: AsyncSession, tenant_id: str, specific_ids: Optional[List[str]], query: Optional[str]
    ) -> List[IncidentCase]:
        stmt = select(IncidentCase).where(
            or_(IncidentCase.tenant_id == tenant_id, IncidentCase.tenant_id.is_(None))
        )
        if specific_ids:
            stmt = stmt.where(
                or_(
                    IncidentCase.case_id.in_(specific_ids),
                    IncidentCase.case_number.in_(specific_ids),
                )
            )
        stmt = stmt.order_by(IncidentCase.created_at.desc()).limit(cls.MAX_RECORDS_PER_TYPE)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    async def _retrieve_assets(
        cls, db: AsyncSession, tenant_id: str, specific_ids: Optional[List[str]], query: Optional[str]
    ) -> List[Asset]:
        stmt = select(Asset).where(Asset.tenant_id == tenant_id)
        if specific_ids:
            stmt = stmt.where(Asset.asset_id.in_(specific_ids))
        stmt = stmt.order_by(Asset.created_at.desc()).limit(cls.MAX_RECORDS_PER_TYPE)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    async def _retrieve_findings(
        cls, db: AsyncSession, tenant_id: str, specific_ids: Optional[List[str]], cve_ids: Optional[List[str]]
    ) -> List[VulnerabilityFinding]:
        stmt = select(VulnerabilityFinding).where(VulnerabilityFinding.tenant_id == tenant_id)
        if specific_ids:
            stmt = stmt.where(VulnerabilityFinding.finding_id.in_(specific_ids))
        if cve_ids:
            stmt = stmt.where(VulnerabilityFinding.cve_id.in_(cve_ids))
        stmt = stmt.order_by(VulnerabilityFinding.created_at.desc()).limit(cls.MAX_RECORDS_PER_TYPE)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    async def _retrieve_cves(cls, db: AsyncSession, cve_ids: List[str]) -> List[CVEFinding]:
        stmt = select(CVEFinding).where(CVEFinding.cve_id.in_(cve_ids)).limit(cls.MAX_RECORDS_PER_TYPE)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    async def _retrieve_stix(
        cls, db: AsyncSession, tenant_id: str, indicators: Optional[List[str]], query: Optional[str]
    ) -> List[StixObject]:
        stmt = select(StixObject).where(
            or_(StixObject.tenant_id == tenant_id, StixObject.tenant_id.is_(None))
        )
        stmt = stmt.order_by(StixObject.created_at.desc()).limit(cls.MAX_RECORDS_PER_TYPE)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    async def _retrieve_custody(cls, db: AsyncSession, tenant_id: str) -> List[ChainOfCustody]:
        stmt = select(ChainOfCustody).where(
            or_(ChainOfCustody.tenant_id == tenant_id, ChainOfCustody.tenant_id.is_(None))
        )
        stmt = stmt.order_by(ChainOfCustody.timestamp.desc()).limit(cls.MAX_RECORDS_PER_TYPE)
        res = await db.execute(stmt)
        return list(res.scalars().all())
