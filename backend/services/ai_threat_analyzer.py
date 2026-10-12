import uuid
from datetime import datetime, timezone
from typing import Dict, Any


class AIThreatAnalyzerService:
    """Generate evidence-aware post-incident summaries.

    This service creates a draft from supplied case information. It does not
    independently verify incident facts or claim that remediation succeeded.
    """

    @staticmethod
    def generate_case_closure_summary(
        case_id: str,
        case_number: str,
        title: str,
        summary: str,
        alerts_count: int = 2,
    ) -> Dict[str, Any]:
        report_id = f"AI-RPT-{uuid.uuid4().hex[:8].upper()}"

        safe_summary = (summary or "").strip()
        if not safe_summary:
            safe_summary = (
                "No incident summary or supporting evidence was provided. "
                "Further investigation is required before drawing conclusions."
            )

        executive_summary = (
            f"Draft summary for incident {case_number} ('{title}'). "
            f"The supplied record reports {max(0, alerts_count)} associated "
            f"alert(s). Detection, containment, and remediation status have "
            f"not been independently verified. Human review is required."
        )

        root_cause_analysis = (
            "Root cause is undetermined from the information supplied. "
            "Do not attribute an attack vector, vulnerability, or threat actor "
            "without supporting evidence. Review the incident record and "
            "associated forensic artifacts before reaching a conclusion."
        )

        lessons_learned = [
            "Document the evidence supporting the incident timeline and conclusions.",
            "Verify containment and remediation actions before marking them complete.",
            "Record unresolved questions and assign follow-up investigation tasks.",
        ]

        return {
            "status": "DRAFT_REQUIRES_REVIEW",
            "report_id": report_id,
            "case_id": case_id,
            "case_number": case_number,
            "executive_summary": executive_summary,
            "root_cause_analysis": root_cause_analysis,
            "lessons_learned": lessons_learned,
            "source_summary": safe_summary,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "human_review_required": True,
        }
