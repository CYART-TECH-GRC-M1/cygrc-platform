import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.evidence import Evidence
from backend.models.control import Control
from backend.models.tenant import TenantStatus


class SIEMControlBridgeService:
    """Connects Module 2 SIEM alert signals to Module 1 Control Status Engine as automated compliance evidence."""

    @staticmethod
    def _to_uuid(val: Any) -> uuid.UUID:
        if isinstance(val, uuid.UUID):
            return val
        try:
            return uuid.UUID(str(val))
        except (ValueError, TypeError):
            return uuid.uuid5(uuid.NAMESPACE_DNS, str(val))

    @classmethod
    def feed_siem_alerts_to_control_engine(
        cls,
        alert_id: str,
        title: str,
        severity: str,
        tenant_id: str,
        control_id: str = "A.5.1"  # Information Security Policies
    ) -> Dict[str, Any]:
        """Stateless backward-compatible signature generating compliance signal dictionary."""
        evidence_id = f"SIEM-EVID-{uuid.uuid4().hex[:8].upper()}"
        compliance_status = "NON_COMPLIANT" if severity in ["HIGH", "CRITICAL"] else "COMPLIANT"

        return {
            "status": "SUCCESS",
            "message": f"SIEM Alert '{title}' ({severity}) converted into automated compliance evidence for Control {control_id}.",
            "control_signal": {
                "evidence_id": evidence_id,
                "tenant_id": tenant_id,
                "control_id": control_id,
                "control_code": control_id,
                "source": "Module 2 (SOC SIEM Real-Time Telemetry)",
                "alert_id": alert_id,
                "alert_severity": severity,
                "calculated_compliance_status": compliance_status,
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    @classmethod
    async def persist_siem_alert_evidence(
        cls,
        db: AsyncSession,
        alert_id: str,
        title: str,
        severity: str,
        tenant_id: str,
        control_code_or_id: str = "A.5.1",
        uploaded_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Durable Phase 9 implementation:
        Resolves the target Control in DB, constructs an immutable Evidence record,
        and commits it to the evidence table.
        """
        parsed_tenant = cls._to_uuid(tenant_id)
        parsed_uploader = cls._to_uuid(uploaded_by or tenant_id)

        # Lookup control by control_code or control_id
        ctrl = None
        try:
            ctrl_uuid = uuid.UUID(control_code_or_id)
            ctrl = await db.get(Control, ctrl_uuid)
        except (ValueError, TypeError):
            pass

        if not ctrl:
            stmt = select(Control).where(Control.control_code == control_code_or_id)
            result = await db.execute(stmt)
            ctrl = result.scalars().first()

        evidence_uuid = uuid.uuid4()
        compliance_status = "NON_COMPLIANT" if severity.upper() in ["HIGH", "CRITICAL"] else "COMPLIANT"

        if ctrl:
            evidence_record = Evidence(
                evidence_id=evidence_uuid,
                tenant_id=parsed_tenant,
                control_id=ctrl.control_id,
                uploaded_by=parsed_uploader,
                title=f"SIEM Alert Telemetry: {title} [{severity.upper()}]",
                description=(
                    f"Automated compliance evidence ingested from SIEM alert {alert_id}. "
                    f"Severity: {severity}. Signal: {compliance_status}."
                ),
                status=TenantStatus.ACTIVE,
                uploaded_at=datetime.utcnow(),
            )
            db.add(evidence_record)
            await db.commit()
            await db.refresh(evidence_record)
            actual_ctrl_id = str(ctrl.control_id)
            actual_ctrl_code = ctrl.control_code
            persisted = True
        else:
            actual_ctrl_id = control_code_or_id
            actual_ctrl_code = control_code_or_id
            persisted = False

        return {
            "status": "SUCCESS",
            "persisted": persisted,
            "message": f"SIEM Alert '{title}' ({severity}) converted into compliance evidence for Control {actual_ctrl_code}.",
            "control_signal": {
                "evidence_id": str(evidence_uuid),
                "tenant_id": str(tenant_id),
                "control_id": actual_ctrl_id,
                "control_code": actual_ctrl_code,
                "source": "Module 2 (SOC SIEM Real-Time Telemetry)",
                "alert_id": alert_id,
                "alert_severity": severity,
                "calculated_compliance_status": compliance_status,
                "timestamp": datetime.utcnow().isoformat(),
            }
        }
