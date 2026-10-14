"""FastAPI routes for Playbook catalogue, execution, and approvals.

Endpoints conform to the existing API versioning scheme (v1). All routes are added under
`/api/v1/playbooks` via the router registration in `backend/api/router.py`.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.dependencies import get_current_user, require_permission
from backend.models.user import User
from backend.playbooks import (
    PlaybookDefinition,
    PlaybookRegistry,
    PlaybookExecutionEngine,
    PlaybookApprovalService,
)
from backend.models.playbook import PlaybookExecution, PlaybookApprovalRecord

router = APIRouter()

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# ---------------------------------------------------------------------------
# Request/Response models
# ---------------------------------------------------------------------------

class ExecutePlaybookRequest(BaseModel):
    inputs: dict = Field(default_factory=dict, description="Playbook input parameters")
    related_alert_id: str | None = None
    related_case_id: str | None = None
    related_finding_id: str | None = None
    related_campaign_id: str | None = None
    target: str | None = None
    target_type: str | None = None

class ExecutionResponse(BaseModel):
    execution_id: str
    status: str
    started_at: str
    current_step: str | None = None
    total_steps: int

class ApproveStepRequest(BaseModel):
    approval_token: str
    decision: str = Field(..., pattern="^(APPROVED|REJECTED)$")
    decision_reason: str | None = None

class ValidateYamlRequest(BaseModel):
    yaml_content: str

class ValidationResult(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)

# ---------------------------------------------------------------------------
# Helper dependencies
# ---------------------------------------------------------------------------

async def get_playbook_or_404(playbook_id: str) -> PlaybookDefinition:
    definition = PlaybookRegistry.get(playbook_id)
    if not definition:
        raise HTTPException(status_code=404, detail=f"Playbook '{playbook_id}' not found.")
    return definition

# ---------------------------------------------------------------------------
# Catalogue endpoints
# ---------------------------------------------------------------------------

@router.get("/", response_model=dict)
async def list_playbooks(
    _: User = Depends(require_permission("playbook:view")),
) -> dict:
    """Return a minimal catalogue of all playbooks.
    The response maps playbook_id → latest version metadata.
    """
    catalogue = PlaybookRegistry.list_latest()
    return catalogue

@router.get("/{playbook_id}", response_model=PlaybookDefinition)
async def get_playbook(
    playbook_id: str,
    _: User = Depends(require_permission("playbook:view")),
) -> PlaybookDefinition:
    return await get_playbook_or_404(playbook_id)

# ---------------------------------------------------------------------------
# Execution endpoints
# ---------------------------------------------------------------------------

@router.post("/{playbook_id}/execute", response_model=ExecutionResponse)
async def start_execution(
    playbook_id: str,
    req: ExecutePlaybookRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("playbook:execute")),
) -> ExecutionResponse:
    definition = await get_playbook_or_404(playbook_id)
    try:
        execution = await PlaybookExecutionEngine.execute_playbook(
            playbook_id=playbook_id,
            inputs=req.inputs,
            actor_id=str(user.id),
            actor_email=user.email,
            actor_role=user.role.value,
            tenant_id=str(user.tenant_id),
            db=db,
            related_alert_id=req.related_alert_id,
            related_case_id=req.related_case_id,
            related_finding_id=req.related_finding_id,
            related_campaign_id=req.related_campaign_id,
            target=req.target,
            target_type=req.target_type,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc))

    return ExecutionResponse(
        execution_id=execution.execution_id,
        status=execution.status,
        started_at=execution.started_at.isoformat() if execution.started_at else None,
        current_step=execution.current_step_id,
        total_steps=execution.total_steps,
    )

@router.get("/executions", response_model=list[ExecutionResponse])
async def list_executions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("playbook:view")),
) -> list[ExecutionResponse]:
    stmt = select(PlaybookExecution).where(PlaybookExecution.tenant_id == str(user.tenant_id))
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [
        ExecutionResponse(
            execution_id=row.execution_id,
            status=row.status,
            started_at=row.started_at.isoformat() if row.started_at else None,
            current_step=row.current_step_id,
            total_steps=row.total_steps,
        )
        for row in rows
    ]

@router.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("playbook:view")),
) -> ExecutionResponse:
    stmt = select(PlaybookExecution).where(
        PlaybookExecution.execution_id == execution_id,
        PlaybookExecution.tenant_id == str(user.tenant_id),
    )
    result = await db.execute(stmt)
    exec_rec = result.scalar_one_or_none()
    if not exec_rec:
        raise HTTPException(status_code=404, detail="Execution not found")
    return ExecutionResponse(
        execution_id=exec_rec.execution_id,
        status=exec_rec.status,
        started_at=exec_rec.started_at.isoformat() if exec_rec.started_at else None,
        current_step=exec_rec.current_step_id,
        total_steps=exec_rec.total_steps,
    )

@router.post("/executions/{execution_id}/approve")
async def approve_step(
    execution_id: str,
    req: ApproveStepRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("playbook:approve")),
) -> dict:
    # Validate token and decision via the approval service
    try:
        await PlaybookApprovalService.process_decision(
            approval_token=req.approval_token,
            decision=req.decision,
            decision_reason=req.decision_reason,
            reviewer=user,
            db=db,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc))

    # After approval, attempt to resume the execution (if still waiting)
    try:
        await PlaybookExecutionEngine.resume_after_approval(
            execution_id=execution_id,
            tenant_id=str(user.tenant_id),
            db=db,
        )
    except Exception as exc:  # noqa: BLE001
        # If the execution is not waiting, just return info
        return {"status": "approval recorded, execution not pending"}

    return {"status": "approval processed and execution resumed"}

@router.post("/executions/{execution_id}/cancel")
async def cancel_execution(
    execution_id: str,
    reason: str = Query(..., description="Reason for cancellation"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("playbook:execute")),
) -> dict:
    try:
        await PlaybookExecutionEngine.cancel_execution(
            execution_id=execution_id,
            tenant_id=str(user.tenant_id),
            reason=reason,
            db=db,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc))
    return {"status": "cancelled"}

@router.get("/approvals/pending", response_model=list[dict])
async def list_pending_approvals(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("playbook:approve")),
) -> list[dict]:
    pending = await PlaybookApprovalService.list_pending(user.tenant_id, db)
    return pending

@router.post("/validate-yaml", response_model=ValidationResult)
async def validate_yaml(req: ValidateYamlRequest) -> ValidationResult:
    try:
        # The schema validation function raises on error
        PlaybookRegistry.validate_yaml_string(req.yaml_content)
        return ValidationResult(valid=True, errors=[])
    except Exception as exc:  # noqa: BLE001
        return ValidationResult(valid=False, errors=[str(exc)])

@router.get("/catalog/rollback")
async def rollback_playbook(
    playbook_id: str,
    version: str,
    user: User = Depends(require_permission("playbook:execute")),
) -> dict:
    try:
        PlaybookRegistry.rollback_to_version(playbook_id, version)
        return {"status": "rolled back", "playbook_id": playbook_id, "version": version}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc))

# End of file

