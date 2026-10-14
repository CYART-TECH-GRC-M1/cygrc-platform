import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.evidence import Evidence
from backend.models.control import Control
from backend.models.risk import Risk
from backend.models.tenant import TenantStatus


class GRCEvidenceBridgeService:
    """Feeds VAPT vulnerability scan findings directly into Module 1 GRC Compliance Control Engine & Risk Register."""

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
        control_code: str = "A.12.6.1"  # Technical Vulnerability Management
    ) -> Dict[str, Any]:
        """Stateless backward-compatible signature generating evidence payload."""
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
            "compliance_signal": "NON_COMPLIANT" if cvss_score >= 7.0 else "COMPLIANT_WITH_RESERVATIONS",
            "timestamp": datetime.utcnow().isoformat()
        }

        return {
            "status": "SUCCESS",
            "message": f"VAPT scan finding {cve_id} successfully mapped to GRC Control {control_code} as automated compliance evidence.",
            "evidence": evidence_payload
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
        Durable Phase 9 implementation:
        1. Resolves Control in DB (e.g. A.12.6.1 Technical Vulnerability Management).
        2. Ingests Evidence record for the control.
        3. If cvss_score >= 7.0 (High/Critical) and create_risk_entry=True, automatically
           registers an item in the Risk Register mapped to the control.
        """
        parsed_tenant = cls._to_uuid(tenant_id)
        parsed_uploader = cls._to_uuid(uploaded_by or tenant_id)

        # Lookup control
        stmt = select(Control).where(Control.control_code == control_code)
        result = await db.execute(stmt)
        ctrl = result.scalars().first()

        evidence_uuid = uuid.uuid4()
        compliance_signal = "NON_COMPLIANT" if cvss_score >= 7.0 else "COMPLIANT_WITH_RESERVATIONS"
        persisted_evidence = False
        persisted_risk_id = None

        if ctrl:
            evidence_record = Evidence(
                evidence_id=evidence_uuid,
                tenant_id=parsed_tenant,
                control_id=ctrl.control_id,
                uploaded_by=parsed_uploader,
                title=f"Automated VAPT Scan Finding [{cve_id}]",
                description=(
                    f"VAPT vulnerability detected on {affected_product}. "
                    f"CVE: {cve_id}, CVSS: {cvss_score}. Status: {compliance_signal}."
                ),
                status=TenantStatus.ACTIVE,
                uploaded_at=datetime.utcnow(),
            )
            db.add(evidence_record)
            persisted_evidence = True

            # If High/Critical CVSS, automatically raise Risk Register item
            if create_risk_entry and cvss_score >= 7.0:
                # Map CVSS to Likelihood (1-5) and Impact (1-5)
                # CVSS 7.0-8.9 -> High (4), 9.0-10.0 -> Critical (5)
                impact_val = 5 if cvss_score >= 9.0 else 4
                likelihood_val = 4  # Confirmed vulnerability on target
                risk_score_val = impact_val * likelihood_val

                risk_record = Risk(
                    risk_id=uuid.uuid4(),
                    tenant_id=parsed_tenant,
                    control_id=ctrl.control_id,
                    title=f"Technical Vulnerability Risk: {cve_id} on {affected_product}",
                    description=(
                        f"Unmitigated high-severity vulnerability {cve_id} (CVSS {cvss_score}) "
                        f"discovered on {affected_product}."
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

            await db.commit()

        evidence_payload = {
            "evidence_id": str(evidence_uuid),
            "tenant_id": str(tenant_id),
            "title": f"Automated VAPT Scan Finding [{cve_id}]",
            "source_module": "Module 2 (Cyber Defense VAPT Engine)",
            "control_code": control_code,
            "cvss_score": cvss_score,
            "affected_product": affected_product,
            "status": "EVIDENCE_ATTACHED" if persisted_evidence else "PROCESSED",
            "compliance_signal": compliance_signal,
            "persisted_evidence": persisted_evidence,
            "created_risk_id": persisted_risk_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        return {
            "status": "SUCCESS",
            "message": f"VAPT scan finding {cve_id} successfully mapped to GRC Control {control_code}.",
            "evidence": evidence_payload,
        }
