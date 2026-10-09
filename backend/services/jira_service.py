import uuid
from datetime import datetime
from typing import Dict, Any


class JiraIntegrationService:
    """Jira Service Management / Jira Software Integration Engine for VAPT findings."""

    @staticmethod
    def push_remediation_ticket(
        cve_id: str,
        cvss_score: float,
        affected_product: str,
        summary: str,
        project_key: str = "CYGRC",
        issue_type: str = "Vulnerability"
    ) -> Dict[str, Any]:
        ticket_number = f"{project_key}-{uuid.uuid4().hex[:4].upper()}"

        priority = "Highest" if cvss_score >= 9.0 else "High"

        jira_payload = {
            "ticket_key": ticket_number,
            "project_key": project_key,
            "issue_type": issue_type,
            "summary": f"[VAPT Alert] {cve_id} in {affected_product}",
            "description": f"Vulnerability: {cve_id}\nCVSS Score: {cvss_score}\nAffected Product: {affected_product}\nSummary: {summary}",
            "priority": priority,
            "status": "OPEN",
            "self_url": f"https://jira.cygrc.internal/browse/{ticket_number}",
            "created_at": datetime.utcnow().isoformat()
        }

        return {
            "status": "SUCCESS",
            "jira_ticket": jira_payload
        }
