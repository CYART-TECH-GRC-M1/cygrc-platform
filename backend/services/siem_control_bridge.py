import uuid
from datetime import datetime
from typing import Dict, Any, List


class SIEMControlBridgeService:
    """Connects Module 2 SIEM alert signals to Module 1 Control Status Engine as automated compliance evidence."""

    @staticmethod
    def feed_siem_alerts_to_control_engine(
        alert_id: str,
        title: str,
        severity: str,
        tenant_id: str,
        control_id: str = "A.5.1"  # Information Security Policies
    ) -> Dict[str, Any]:
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
