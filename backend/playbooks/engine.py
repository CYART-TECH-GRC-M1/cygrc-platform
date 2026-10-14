"""Durable Playbook Execution Engine for CyGRC.

Implements:
1. Durable execution records persisted to PostgreSQL / SQLite.
2. Sequential step execution with per-step retry logic.
3. Human-in-the-loop approval gates for SENSITIVE_DISRUPTIVE / DESTRUCTIVE steps.
4. Cancellation, timeout, and resume-after-approval semantics.
5. Evidence reference accumulation across steps.
6. Anti-bypass: a failed required step always marks the entire execution FAILED.
7. Tenant isolation: every action call carries the originating tenant_id.

Execution lifecycle
-------------------
PENDING → RUNNING → {WAITING_FOR_APPROVAL | COMPLETED | FAILED | CANCELLED | TIMED_OUT}

When an approval gate is hit:
  RUNNING → WAITING_FOR_APPROVAL   (engine returns; execution paused in DB)
  (human submits decision via API)
  WAITING_FOR_APPROVAL → RUNNING   (resume_after_approval called)
  RUNNING → COMPLETED | FAILED
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.playbook import PlaybookApprovalRecord, PlaybookExecution
from backend.playbooks.actions import PlaybookActionHandlers
from backend.playbooks.approvals import PlaybookApprovalService
from backend.playbooks.registry import PlaybookRegistry
from backend.playbooks.schema import (
    PlaybookDefinition,
    PlaybookStep,
    StepClassification,
)

logger = logging.getLogger("cygrc.playbooks.engine")

# Classifications that require a human gate before execution
_APPROVAL_REQUIRED = {StepClassification.SENSITIVE_DISRUPTIVE, StepClassification.DESTRUCTIVE}


class PlaybookExecutionError(Exception):
    """Raised when an execution cannot be started or resumed due to a state error."""


class PlaybookExecutionEngine:
    """Stateless engine — all durable state is persisted in the PlaybookExecution record."""

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    @classmethod
    async def execute_playbook(
        cls,
        playbook_id: str,
        inputs: Dict[str, Any],
        actor_id: str,
        actor_email: str,
        actor_role: str,
        tenant_id: str,
        db: AsyncSession,
        *,
        related_alert_id: Optional[str] = None,
        related_case_id: Optional[str] = None,
        related_finding_id: Optional[str] = None,
        related_campaign_id: Optional[str] = None,
        target: Optional[str] = None,
        target_type: Optional[str] = None,
    ) -> PlaybookExecution:
        """Create and run a new playbook execution.

        Returns the execution record. If an approval gate is hit the record will
        be in WAITING_FOR_APPROVAL status and the caller should return the record
        to the client for the human-in-the-loop flow.
        """
        # Load and validate playbook definition
        definition = PlaybookRegistry.get(playbook_id)
        if definition is None:
            raise PlaybookExecutionError(f"Playbook '{playbook_id}' not found in catalogue.")

        # Validate inputs against declared schema
        validated_inputs = cls._validate_inputs(definition, inputs)

        now = datetime.now(timezone.utc)

        # Create durable execution record
        execution = PlaybookExecution(
            tenant_id=tenant_id,
            playbook_id=playbook_id,
            playbook_version=definition.version,
            playbook_name=definition.name,
            discipline=definition.discipline.value,
            actor_id=actor_id,
            actor_email=actor_email,
            actor_role=actor_role,
            target=target or validated_inputs.get("target"),
            target_type=target_type or validated_inputs.get("target_type"),
            related_alert_id=related_alert_id,
            related_case_id=related_case_id,
            related_finding_id=related_finding_id,
            related_campaign_id=related_campaign_id,
            inputs=validated_inputs,
            current_step_index=0,
            total_steps=len(definition.steps),
            status="RUNNING",
            step_results=[],
            evidence_references=[],
            approval_state={},
            errors=[],
            started_at=now,
            created_at=now,
            updated_at=now,
        )

        db.add(execution)
        await db.commit()
        await db.refresh(execution)

        logger.info(
            "Started playbook execution '%s' for playbook '%s' v%s (tenant: %s, actor: %s)",
            execution.execution_id, playbook_id, definition.version, tenant_id, actor_email,
        )

        # Run the step loop
        await cls._run_steps(execution, definition, tenant_id, db)
        return execution

    @classmethod
    async def resume_after_approval(
        cls,
        execution_id: str,
        tenant_id: str,
        db: AsyncSession,
    ) -> PlaybookExecution:
        """Resume an execution that was paused at an approval gate.

        Called by the approvals endpoint after a PENDING approval is set to APPROVED.
        """
        execution = await cls._load_execution(execution_id, tenant_id, db)

        if execution.status != "WAITING_FOR_APPROVAL":
            raise PlaybookExecutionError(
                f"Execution '{execution_id}' is not in WAITING_FOR_APPROVAL state "
                f"(current: {execution.status})."
            )

        # Verify that the blocking approval has been granted
        approval = await cls._get_pending_approval(execution_id, db)
        if approval is not None:
            raise PlaybookExecutionError(
                f"Execution '{execution_id}' still has a PENDING approval for step "
                f"'{approval.step_id}'. Cannot resume until approved or rejected."
            )

        # Check if any approval was rejected — if so, fail the execution
        rejected = await cls._get_rejected_approval(execution_id, db)
        if rejected is not None:
            await cls._fail_execution(
                execution,
                f"Approval rejected for step '{rejected.step_id}' by '{rejected.reviewed_by}': "
                f"{rejected.decision_reason or 'No reason given.'}",
                db,
            )
            return execution

        # Load the playbook definition and resume from the current step index
        definition = PlaybookRegistry.get(execution.playbook_id)
        if definition is None:
            await cls._fail_execution(
                execution,
                f"Playbook '{execution.playbook_id}' no longer in catalogue.",
                db,
            )
            return execution

        execution.status = "RUNNING"
        await db.commit()

        await cls._run_steps(execution, definition, tenant_id, db)
        return execution

    @classmethod
    async def cancel_execution(
        cls,
        execution_id: str,
        tenant_id: str,
        reason: str,
        db: AsyncSession,
    ) -> PlaybookExecution:
        """Cancel an in-progress or waiting execution."""
        execution = await cls._load_execution(execution_id, tenant_id, db)

        if execution.status in {"COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"}:
            raise PlaybookExecutionError(
                f"Execution '{execution_id}' is already terminal (status: {execution.status})."
            )

        now = datetime.now(timezone.utc)
        execution.status = "CANCELLED"
        execution.completed_at = now
        execution.updated_at = now
        errors_list = list(execution.errors or [])
        errors_list.append({"type": "CANCELLED", "message": reason, "at": now.isoformat()})
        execution.errors = errors_list
        await db.commit()
        await db.refresh(execution)
        logger.info("Execution '%s' cancelled: %s", execution_id, reason)
        return execution

    # -------------------------------------------------------------------------
    # Internal step loop
    # -------------------------------------------------------------------------

    @classmethod
    async def _run_steps(
        cls,
        execution: PlaybookExecution,
        definition: PlaybookDefinition,
        tenant_id: str,
        db: AsyncSession,
    ) -> None:
        """Execute steps sequentially from current_step_index."""
        steps = definition.steps
        start_idx = execution.current_step_index

        for idx in range(start_idx, len(steps)):
            step = steps[idx]
            now = datetime.now(timezone.utc)

            # Update position in DB
            execution.current_step_id = step.id
            execution.current_step_index = idx
            execution.updated_at = now
            await db.commit()

            classification = step.classification

            # ---- Approval gate ----
            if classification in _APPROVAL_REQUIRED:
                # Check if there is already a granted approval for this step
                granted = await cls._get_step_approval(execution.execution_id, step.id, db)
                if granted is None:
                    # No prior approval — pause and request one
                    required_role = cls._required_approver_role(classification, definition)
                    action_scope = {
                        "step_id": step.id,
                        "action": step.action,
                        "params": step.parameters or {},
                        "playbook_id": definition.id,
                        "playbook_version": definition.version,
                        "tenant_id": tenant_id,
                    }
                    await PlaybookApprovalService.create_approval_request(
                        execution=execution,
                        step_id=step.id,
                        step_name=step.name,
                        classification=classification,
                        action_type=step.action,
                        required_role=required_role,
                        target=execution.target,
                        action_scope=action_scope,
                        db=db,
                    )
                    execution.status = "WAITING_FOR_APPROVAL"
                    approval_state = dict(execution.approval_state or {})
                    approval_state[step.id] = "PENDING"
                    execution.approval_state = approval_state
                    execution.updated_at = now
                    await db.commit()
                    await db.refresh(execution)
                    logger.info(
                        "Execution '%s' paused at step '%s' awaiting approval.",
                        execution.execution_id, step.id,
                    )
                    return  # Pause — will be resumed via resume_after_approval

                elif granted.status == "REJECTED":
                    await cls._fail_execution(
                        execution,
                        f"Step '{step.id}' approval was rejected by '{granted.reviewed_by}'.",
                        db,
                    )
                    return

                else:
                    # APPROVED — record it and continue
                    approval_state = dict(execution.approval_state or {})
                    approval_state[step.id] = "APPROVED"
                    execution.approval_state = approval_state

            # ---- Execute the step ----
            step_result = await cls._execute_step_with_retry(step, execution, tenant_id, db)

            # Accumulate results and evidence
            results_list = list(execution.step_results or [])
            results_list.append(step_result)
            execution.step_results = results_list

            if step_result.get("evidence_reference"):
                evidence_list = list(execution.evidence_references or [])
                evidence_list.append(step_result["evidence_reference"])
                execution.evidence_references = evidence_list

            # A failed required step fails the whole playbook
            if not step_result.get("success") and not step.optional:
                errors_list = list(execution.errors or [])
                errors_list.append({
                    "step_id": step.id,
                    "error": step_result.get("error", "Step failed without an error message."),
                    "at": now.isoformat(),
                })
                execution.errors = errors_list
                await cls._fail_execution(
                    execution,
                    f"Required step '{step.id}' failed: {step_result.get('error', 'unknown')}",
                    db,
                )
                return

            execution.updated_at = now
            await db.commit()

        # All steps completed
        now = datetime.now(timezone.utc)
        execution.status = "COMPLETED"
        execution.completed_at = now
        execution.current_step_index = len(steps)
        execution.updated_at = now
        await db.commit()
        await db.refresh(execution)
        logger.info(
            "Execution '%s' completed successfully (%d steps).",
            execution.execution_id, len(steps),
        )

    @classmethod
    async def _execute_step_with_retry(
        cls,
        step: "PlaybookStep",
        execution: PlaybookExecution,
        tenant_id: str,
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """Execute one step, honouring its retry policy."""
        retry_policy = step.retry_policy
        max_retries = retry_policy.max_retries if retry_policy else 1
        backoff = retry_policy.backoff_seconds if retry_policy else 1.0

        merged_params = dict(step.parameters or {})
        merged_params.update(execution.inputs or {})
        # Inject runtime context
        merged_params["_tenant_id"] = tenant_id
        merged_params["_execution_id"] = execution.execution_id
        merged_params["_target"] = execution.target

        attempt = 0
        last_result = None

        while attempt <= max_retries:
            try:
                timeout_s = step.timeout_seconds if step.timeout_seconds else 120
                result = await asyncio.wait_for(
                    PlaybookActionHandlers.execute_action(step.action, merged_params, tenant_id, db),
                    timeout=float(timeout_s),
                )
                last_result = {
                    "step_id": step.id,
                    "step_name": step.name,
                    "action": step.action,
                    "attempt": attempt + 1,
                    "success": result.success,
                    "output": result.output,
                    "error": result.error,
                    "evidence_reference": result.evidence_reference,
                    "executed_at": datetime.now(timezone.utc).isoformat(),
                }
                if result.success:
                    logger.info(
                        "Step '%s' succeeded on attempt %d for execution '%s'.",
                        step.id, attempt + 1, execution.execution_id,
                    )
                    return last_result

                logger.warning(
                    "Step '%s' failed on attempt %d: %s",
                    step.id, attempt + 1, result.error,
                )

            except asyncio.TimeoutError:
                error_msg = f"Step '{step.id}' timed out after {timeout_s}s."
                logger.warning(error_msg)
                last_result = {
                    "step_id": step.id,
                    "step_name": step.name,
                    "action": step.action,
                    "attempt": attempt + 1,
                    "success": False,
                    "output": {},
                    "error": error_msg,
                    "evidence_reference": None,
                    "executed_at": datetime.now(timezone.utc).isoformat(),
                }

            except Exception as exc:  # noqa: BLE001
                error_msg = f"Step '{step.id}' raised exception: {exc!r}"
                logger.exception(error_msg)
                last_result = {
                    "step_id": step.id,
                    "step_name": step.name,
                    "action": step.action,
                    "attempt": attempt + 1,
                    "success": False,
                    "output": {},
                    "error": error_msg,
                    "evidence_reference": None,
                    "executed_at": datetime.now(timezone.utc).isoformat(),
                }

            attempt += 1
            if attempt <= max_retries:
                await asyncio.sleep(backoff)

        return last_result or {
            "step_id": step.id,
            "step_name": step.name,
            "action": step.action,
            "attempt": attempt,
            "success": False,
            "output": {},
            "error": "All retry attempts exhausted.",
            "evidence_reference": None,
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _validate_inputs(
        definition: PlaybookDefinition, inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and coerce caller-supplied inputs against declared input schema."""
        validated: Dict[str, Any] = {}
        for inp in definition.inputs:
            val = inputs.get(inp.name)
            if val is None and inp.default is not None:
                val = inp.default
            if val is None and inp.required:
                raise PlaybookExecutionError(
                    f"Required input '{inp.name}' not supplied for playbook '{definition.id}'."
                )
            if val is not None:
                # Basic type coercion
                if inp.type == "integer":
                    try:
                        val = int(val)
                    except (TypeError, ValueError) as exc:
                        raise PlaybookExecutionError(
                            f"Input '{inp.name}' must be an integer."
                        ) from exc
                elif inp.type == "boolean":
                    if isinstance(val, str):
                        val = val.lower() in {"true", "1", "yes"}
                validated[inp.name] = val
        # Pass through any extra inputs not declared (e.g. target)
        for k, v in inputs.items():
            if k not in validated:
                validated[k] = v
        return validated

    @staticmethod
    def _required_approver_role(
        classification: StepClassification, definition: PlaybookDefinition
    ) -> str:
        """Map step classification to the minimum approver role."""
        if classification == StepClassification.DESTRUCTIVE:
            return "Platform Operator"
        # SENSITIVE_DISRUPTIVE → discipline-specific lead
        discipline_leads = {
            "SOC": "SOC Lead",
            "VAPT": "VAPT Lead",
            "DFIR": "DFIR Lead",
            "RED_TEAM": "Red Team Lead",
        }
        return discipline_leads.get(definition.discipline.value, "SOC Lead")

    @staticmethod
    async def _load_execution(
        execution_id: str, tenant_id: str, db: AsyncSession
    ) -> PlaybookExecution:
        stmt = select(PlaybookExecution).where(
            PlaybookExecution.execution_id == execution_id,
            PlaybookExecution.tenant_id == tenant_id,
        )
        result = await db.execute(stmt)
        execution = result.scalar_one_or_none()
        if execution is None:
            raise PlaybookExecutionError(
                f"Execution '{execution_id}' not found for tenant '{tenant_id}'."
            )
        return execution

    @staticmethod
    async def _get_pending_approval(
        execution_id: str, db: AsyncSession
    ) -> Optional[PlaybookApprovalRecord]:
        stmt = select(PlaybookApprovalRecord).where(
            PlaybookApprovalRecord.execution_id == execution_id,
            PlaybookApprovalRecord.status == "PENDING",
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def _get_rejected_approval(
        execution_id: str, db: AsyncSession
    ) -> Optional[PlaybookApprovalRecord]:
        stmt = select(PlaybookApprovalRecord).where(
            PlaybookApprovalRecord.execution_id == execution_id,
            PlaybookApprovalRecord.status == "REJECTED",
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def _get_step_approval(
        execution_id: str, step_id: str, db: AsyncSession
    ) -> Optional[PlaybookApprovalRecord]:
        """Return the approval record for this specific step (any status)."""
        stmt = select(PlaybookApprovalRecord).where(
            PlaybookApprovalRecord.execution_id == execution_id,
            PlaybookApprovalRecord.step_id == step_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def _fail_execution(
        execution: PlaybookExecution,
        reason: str,
        db: AsyncSession,
    ) -> None:
        now = datetime.now(timezone.utc)
        execution.status = "FAILED"
        execution.completed_at = now
        execution.updated_at = now
        errors_list = list(execution.errors or [])
        errors_list.append({"type": "ENGINE_FAILURE", "message": reason, "at": now.isoformat()})
        execution.errors = errors_list
        await db.commit()
        await db.refresh(execution)
        logger.error("Execution '%s' FAILED: %s", execution.execution_id, reason)

