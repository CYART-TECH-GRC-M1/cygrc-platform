
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.evidence import Evidence
from backend.models.control import Control
from backend.models.risk import Risk
from backend.models.tenant import TenantStatus
from backend.models.tenant_control import TenantControlMapping


class GRCEvidenceBridgeService:
    """Feeds VAPT findings into the GRC Evidence and Risk Register."""

    @staticmethod
    def _to_uuid(val: Any) -> uuid.UUID:
        if isinstance(val, uuid.UUID):
            return val
        try:
            return uuid.UUID(str(val))
        except (ValueError, TypeError):
            return uuid.uuid5(uuid.NAMESPACE_DNS, str(val))

    @classmethod
    def feed_vapt_to_grc(
        cls,
        cve_id: str,
        cvss_score: float,
        affected_product: str,
        tenant_id: str,
        control_code: str = "A.12.6.1",
    ) -> Dict[str, Any]:
        """Stateless backward-compatible evidence payload."""
        evidence_id = f"EVID-GRC-{uuid.uuid4().hex[:8].upper()}"

        evidence_payload = {
            "evidence_id": evidence_id,
            "tenant_id": tenant_id,
            "title": f"Automated VAPT Scan Finding [{cve_id}]",
            "source_module": "Module 2 (Cyber Defense VAPT Engine)",
            "control_code": control_code,
            "cvss_score": cvss_score,
            "affected_product": affected_product,
            "status": "EVIDENCE_ATTACHED",
            "compliance_signal": (
                "NON_COMPLIANT"
                if cvss_score >= 7.0
                else "COMPLIANT_WITH_RESERVATIONS"
            ),
            "timestamp": datetime.utcnow().isoformat(),
        }

        return {
            "status": "SUCCESS",
            "message": (
                f"VAPT scan finding {cve_id} mapped to GRC Control "
                f"{control_code} as automated compliance evidence."
            ),
            "evidence": evidence_payload,
        }

    @classmethod
    async def persist_vapt_evidence_and_risk(
        cls,
        db: AsyncSession,
        cve_id: str,
        cvss_score: float,
        affected_product: str,
        tenant_id: str,
        control_code: str = "A.12.6.1",
        uploaded_by: Optional[str] = None,
        create_risk_entry: bool = True,
    ) -> Dict[str, Any]:
        """
        Persist VAPT evidence and optionally create a risk entry.

        The control must be actively mapped to the specified tenant.
        High/Critical findings (CVSS >= 7.0) create a risk entry when
        create_risk_entry is True.
        """
        parsed_tenant = cls._to_uuid(tenant_id)
        parsed_uploader = cls._to_uuid(uploaded_by or tenant_id)

        # Find the control only if it is actively mapped to this tenant.
        stmt = (
            select(Control)
            .join(
                TenantControlMapping,
                TenantControlMapping.control_id == Control.control_id,
            )
            .where(
                Control.control_code == control_code,
                TenantControlMapping.tenant_id == parsed_tenant,
                TenantControlMapping.status == "ACTIVE",
            )
        )

        result = await db.execute(stmt)
        ctrl = result.scalars().first()

        # Do not report success if the tenant has no active control mapping.
        if ctrl is None:
            return {
                "status": "ERROR",
                "message": (
                    f"Control {control_code} is not mapped to tenant "
                    f"{parsed_tenant} or its mapping is inactive."
                ),
                "evidence": None,
            }

        evidence_uuid = uuid.uuid4()
        compliance_signal = (
            "NON_COMPLIANT"
            if cvss_score >= 7.0
            else "COMPLIANT_WITH_RESERVATIONS"
        )

        evidence_record = Evidence(
            evidence_id=evidence_uuid,
            tenant_id=parsed_tenant,
            control_id=ctrl.control_id,
            uploaded_by=parsed_uploader,
            title=f"Automated VAPT Scan Finding [{cve_id}]",
            description=(
                f"VAPT vulnerability detected on {affected_product}. "
                f"CVE: {cve_id}, CVSS: {cvss_score}. "
                f"Status: {compliance_signal}."
            ),
            status=TenantStatus.ACTIVE,
            uploaded_at=datetime.utcnow(),
        )
        db.add(evidence_record)

        persisted_risk_id = None

        # Create a Risk Register entry for High/Critical findings.
        if create_risk_entry and cvss_score >= 7.0:
            impact_val = 5 if cvss_score >= 9.0 else 4
            likelihood_val = 4
            risk_score_val = impact_val * likelihood_val

            risk_record = Risk(
                risk_id=uuid.uuid4(),
                tenant_id=parsed_tenant,
                control_id=ctrl.control_id,
                title=(
                    f"Technical Vulnerability Risk: {cve_id} "
                    f"on {affected_product}"
                ),
                description=(
                    f"Unmitigated high-severity vulnerability {cve_id} "
                    f"(CVSS {cvss_score}) discovered on {affected_product}."
                ),
                likelihood=likelihood_val,
                impact=impact_val,
                risk_score=risk_score_val,
                status=TenantStatus.ACTIVE,
                created_by=parsed_uploader,
                created_at=datetime.utcnow(),
            )
            db.add(risk_record)
            await db.flush()
            persisted_risk_id = str(risk_record.risk_id)

        # Save the evidence and risk entry together.
        await db.commit()

        evidence_payload = {
            "evidence_id": str(evidence_uuid),
            "tenant_id": str(parsed_tenant),
            "title": f"Automated VAPT Scan Finding [{cve_id}]",
            "source_module": "Module 2 (Cyber Defense VAPT Engine)",
            "control_code": control_code,
            "cvss_score": cvss_score,
            "affected_product": affected_product,
            "status": "EVIDENCE_ATTACHED",
            "compliance_signal": compliance_signal,
            "persisted_evidence": True,
            "created_risk_id": persisted_risk_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        return {
            "status": "SUCCESS",
            "message": (
                f"VAPT scan finding {cve_id} successfully mapped to "
                f"GRC Control {control_code}."
            ),
            "evidence": evidence_payload,
        }