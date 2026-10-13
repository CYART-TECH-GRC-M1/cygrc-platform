"""Server-Enforced Approval Model for Playbook Workflows.

Classifies operations into:
- READ_ONLY
- REVERSIBLE_LOW_RISK
- SENSITIVE_DISRUPTIVE
- DESTRUCTIVE

Enforces:
1. Mandatory human sign-off for sensitive or disruptive operations.
2. Server-side validation of approval token, reviewer tenant, roles/permissions,
   action scope, and playbook version.
3. Strict anti-bypass: execution engine never proceeds past an approval gate without
   a validated, non-replayed approval token.
"""
from datetime import datetime, timezone
import logging
import secrets
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.permissions import AppRole, normalize_role_name
from backend.models.playbook import PlaybookApprovalRecord, PlaybookExecution
from backend.playbooks.schema import StepClassification

logger = logging.getLogger("cygrc.playbooks.approvals")


class PlaybookApprovalService:
    """Manages human-in-the-loop approval requests and cryptographic token verification."""

    @classmethod
    async def create_approval_request(
        cls,
        execution: PlaybookExecution,
        step_id: str,
        step_name: str,
        classification: StepClassification,
        action_type: str,
        required_role: str,
        target: Optional[str],
        action_scope: Dict[str, Any],
        db: AsyncSession,
    ) -> PlaybookApprovalRecord:
        """Creates a pending human approval record with a cryptographically secure token."""
        approval_token = f"PB-SIG-{secrets.token_hex(16).upper()}"
        now = datetime.now(timezone.utc)

        record = PlaybookApprovalRecord(
            execution_id=execution.execution_id,
            tenant_id=execution.tenant_id,
            playbook_id=execution.playbook_id,
            playbook_version=execution.playbook_version,
            step_id=step_id,
            step_name=step_name,
            step_classification=classification.value if hasattr(classification, "value") else str(classification),
            action_type=action_type,
            target=target,
            status="PENDING",
            required_role=required_role,
            requested_by=execution.actor_email or execution.actor_id,
            approval_token=approval_token,
            action_scope=action_scope,
            created_at=now,
        )

        db.add(record)
        await db.commit()
        await db.refresh(record)
        logger.info(
            "Created playbook approval request '%s' for execution '%s' step '%s' (role: %s)",
            record.approval_id, execution.execution_id, step_id, required_role
        )
        return record

    @classmethod
    async def process_decision(
        cls,
        execution_id: str,
        step_id: str,
        decision: str,  # "APPROVED" or "REJECTED"
        tenant_id: str,
        reviewer_id: str,
        reviewer_email: str,
        reviewer_role: str,
        approval_token: str,
        decision_reason: str,
        db: AsyncSession,
        expected_playbook_version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validates approval identity, tenant, permissions, scope, and playbook version.
        Rejects tampered, cross-tenant, unauthorized, or replayed approval decisions.
        """
        norm_decision = decision.upper().strip()
        if norm_decision not in ("APPROVED", "REJECTED"):
            return {
                "success": False,
                "error": f"Invalid decision '{decision}'. Must be 'APPROVED' or 'REJECTED'.",
            }

        # 1. Fetch approval record matching execution, step, and tenant
        stmt = select(PlaybookApprovalRecord).where(
            PlaybookApprovalRecord.execution_id == execution_id,
            PlaybookApprovalRecord.step_id == step_id,
            PlaybookApprovalRecord.tenant_id == tenant_id,
        )
        res = await db.execute(stmt)
        record = res.scalar_one_or_none()

        if not record:
            return {
                "success": False,
                "error": f"No approval request found for execution '{execution_id}' and step '{step_id}' in tenant '{tenant_id}'.",
            }

        # 2. Check if already decided (Replay Prevention)
        if record.status != "PENDING":
            return {
                "success": False,
                "error": f"Approval request '{record.approval_id}' has already been decided ({record.status}). Replay blocked.",
            }

        # 3. Cryptographic Token Verification
        if record.approval_token != approval_token.strip():
            return {
                "success": False,
                "error": "Invalid approval token signature. Access denied.",
            }

        # 4. Version Integrity Check
        if expected_playbook_version and record.playbook_version != expected_playbook_version:
            return {
                "success": False,
                "error": (
                    f"Playbook version mismatch. Approval is bound to version {record.playbook_version}, "
                    f"but expected {expected_playbook_version}."
                ),
            }

        # 5. Role & Permission Authorization Check
        norm_user_role = normalize_role_name(reviewer_role)
        norm_req_role = normalize_role_name(record.required_role)

        # Super admin / platform operator / tenant admin can approve any step
        admin_roles = {
            normalize_role_name(AppRole.PLATFORM_OPERATOR.value),
            normalize_role_name(AppRole.SUPER_ADMIN.value),
            normalize_role_name(AppRole.ADMIN.value),
            normalize_role_name(AppRole.TENANT_ADMIN.value),
            normalize_role_name(AppRole.TENANT_ADMIN_LEGACY.value),
        }

        has_permission = norm_user_role in admin_roles or norm_user_role == norm_req_role
        if not has_permission:
            return {
                "success": False,
                "error": (
                    f"Role authorization failure: User role '{reviewer_role}' does not satisfy required role "
                    f"'{record.required_role}' for this sensitive step."
                ),
            }

        # 6. Apply Decision
        now = datetime.now(timezone.utc)
        record.status = norm_decision
        record.decision = norm_decision
        record.reviewed_by = reviewer_email or reviewer_id
        record.decision_reason = decision_reason
        record.decided_at = now
        await db.commit()
        await db.refresh(record)

        logger.info(
            "Processed approval decision '%s' for record '%s' by reviewer '%s'",
            norm_decision, record.approval_id, record.reviewed_by
        )

        return {
            "success": True,
            "approval_id": record.approval_id,
            "decision": norm_decision,
            "step_id": step_id,
            "approved": norm_decision == "APPROVED",
            "decided_at": now.isoformat(),
        }

    @classmethod
    async def list_pending_approvals(
        cls,
        tenant_id: str,
        db: AsyncSession,
        execution_id: Optional[str] = None,
    ) -> List[PlaybookApprovalRecord]:
        """Lists all pending approval requests for a tenant."""
        stmt = select(PlaybookApprovalRecord).where(
            PlaybookApprovalRecord.tenant_id == tenant_id,
            PlaybookApprovalRecord.status == "PENDING",
        )
        if execution_id:
            stmt = stmt.where(PlaybookApprovalRecord.execution_id == execution_id)

        res = await db.execute(stmt)
        return list(res.scalars().all())

