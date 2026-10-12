import hashlib
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.models.campaign import AtomicTestExecution, DetectionVerificationRecord
from backend.services.atomic_runner import AtomicRunnerService
from backend.services.caldera_service import CalderaService
from backend.services.detection_verification import DetectionVerificationService

router = APIRouter()

# In-memory execution log fallback for legacy test compatibility
_ATOMIC_EXECUTION_HISTORY: List[Dict[str, Any]] = []


class AtomicExecutionRequest(BaseModel):
    technique_id: str  # e.g., "T1059.001"
    technique_name: str  # e.g., "PowerShell Execution"
    target_asset_id: str
    executor: str = "powershell"  # powershell, cmd, sh, bash
    command: Optional[str] = None
    campaign_id: Optional[str] = None
    operator_id: Optional[str] = "atomic-operator"


class AtomicExecutionResponse(BaseModel):
    execution_id: str
    tenant_id: str
    technique_id: str
    technique_name: str
    target_asset_id: str
    executor: str
    status: str
    execution_log: str
    execution_hash: str
    timestamp: datetime

    class Config:
        from_attributes = True


class CalderaOperationCreateRequest(BaseModel):
    name: str
    adversary_id: str  # e.g., "adv-discovery-01"
    target_asset_id: str
    operator_id: Optional[str] = "caldera-operator"
    campaign_id: Optional[str] = None
    agent_paw: Optional[str] = None


class DetectionVerifyRequest(BaseModel):
    execution_id: str
    technique_id: str
    campaign_id: Optional[str] = None
    target_asset_id: Optional[str] = None


class ManualVerifyRequest(BaseModel):
    verification_id: str
    analyst_name: str
    notes: str
    status: str = "MANUALLY_VERIFIED"


# ============================================================================
# Atomic Red Team Endpoints
# ============================================================================


@router.post("/atomic/execute", response_model=AtomicExecutionResponse, status_code=status.HTTP_200_OK)
async def execute_atomic_test(
    payload: AtomicExecutionRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Executes an Atomic Red Team single-technique security control validation test.
    Validates target authorization, executes benign process in sandbox, captures
    real process exit code, outputs, and persists to DB.
    """
    try:
        record = await AtomicRunnerService.execute_test(
            db=db,
            tenant_id=tenant_id,
            technique_id=payload.technique_id,
            technique_name=payload.technique_name,
            target_asset_id=payload.target_asset_id,
            executor=payload.executor,
            custom_command=payload.command,
            campaign_id=payload.campaign_id,
            operator_id=payload.operator_id,
        )

        resp = AtomicExecutionResponse(
            execution_id=record.execution_id,
            tenant_id=record.tenant_id,
            technique_id=record.technique_id,
            technique_name=record.technique_name,
            target_asset_id=record.target_asset_id,
            executor=record.executor,
            status=record.status,
            execution_log=record.execution_log,
            execution_hash=record.execution_hash,
            timestamp=record.timestamp,
        )

        # Maintain in-memory mirror for backward compatibility
        _ATOMIC_EXECUTION_HISTORY.append({
            "execution_id": resp.execution_id,
            "tenant_id": resp.tenant_id,
            "technique_id": resp.technique_id,
            "technique_name": resp.technique_name,
            "target_asset_id": resp.target_asset_id,
            "executor": resp.executor,
            "status": resp.status,
            "execution_log": resp.execution_log,
            "execution_hash": resp.execution_hash,
            "timestamp": resp.timestamp,
        })

        return resp
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")


@router.get("/atomic/history", response_model=List[AtomicExecutionResponse])
async def list_atomic_executions(
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """
    List persistent execution history of Atomic Red Team tests from database.
    Replaces volatile in-memory storage (DATA-02).
    """
    stmt = (
        select(AtomicTestExecution)
        .where(AtomicTestExecution.tenant_id == tenant_id)
        .order_by(AtomicTestExecution.timestamp.desc())
    )
    res = await db.execute(stmt)
    db_records = res.scalars().all()

    if db_records:
        return [
            AtomicExecutionResponse(
                execution_id=r.execution_id,
                tenant_id=r.tenant_id,
                technique_id=r.technique_id,
                technique_name=r.technique_name,
                target_asset_id=r.target_asset_id,
                executor=r.executor,
                status=r.status,
                execution_log=r.execution_log,
                execution_hash=r.execution_hash,
                timestamp=r.timestamp,
            )
            for r in db_records
        ]

    # Fallback to in-memory list
    return [e for e in _ATOMIC_EXECUTION_HISTORY if e.get("tenant_id") == tenant_id]


@router.get("/atomic/catalog")
async def get_atomic_catalog():
    """Returns trusted, approved Atomic Red Team test catalog."""
    return AtomicRunnerService.get_catalog()


# ============================================================================
# Caldera Integration Endpoints
# ============================================================================


@router.get("/caldera/health")
async def get_caldera_health():
    """Performs health check on configured Caldera instance."""
    return await CalderaService.check_health()


@router.get("/caldera/profiles")
async def get_caldera_profiles():
    """Returns approved adversary profiles catalogue."""
    return CalderaService.get_approved_profiles()


@router.post("/caldera/operations", status_code=status.HTTP_201_CREATED)
async def create_caldera_operation(
    payload: CalderaOperationCreateRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Creates an approved Caldera operation.
    Validates target authorization and adversary profile.
    """
    try:
        op = await CalderaService.create_operation(
            db=db,
            tenant_id=tenant_id,
            name=payload.name,
            adversary_id=payload.adversary_id,
            target_asset_id=payload.target_asset_id,
            operator_id=payload.operator_id or "caldera-operator",
            campaign_id=payload.campaign_id,
            agent_paw=payload.agent_paw,
        )
        return op
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/caldera/operations/{operation_id}")
async def poll_caldera_operation(
    operation_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Polls operation execution state."""
    try:
        return await CalderaService.poll_operation_status(operation_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/caldera/operations/{operation_id}/results")
async def get_caldera_operation_results(
    operation_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves actual task results for operation.
    Evaluates individual task statuses without reporting false-positive success.
    """
    try:
        return await CalderaService.get_operation_results(db=db, operation_id=operation_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/caldera/operations/{operation_id}/cancel")
async def cancel_caldera_operation(
    operation_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Cancels a running Caldera operation."""
    try:
        return await CalderaService.cancel_operation(db=db, tenant_id=tenant_id, operation_id=operation_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# Detection Verification & Purple Team Endpoints
# ============================================================================


@router.post("/detection/verify")
async def verify_execution_detection(
    payload: DetectionVerifyRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Correlates a test execution with actual SOC alerts and telemetry.
    Identifies whether the technique was DETECTED or represents a detection GAP.
    """
    record = await DetectionVerificationService.correlate_execution(
        db=db,
        tenant_id=tenant_id,
        execution_id=payload.execution_id,
        technique_id=payload.technique_id,
        campaign_id=payload.campaign_id,
        target_asset_id=payload.target_asset_id,
    )
    return record


@router.post("/detection/manual-verify")
async def manual_analyst_verification(
    payload: ManualVerifyRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Allows a SOC analyst to manually sign off or update detection verification."""
    try:
        record = await DetectionVerificationService.manually_verify(
            db=db,
            tenant_id=tenant_id,
            verification_id=payload.verification_id,
            analyst_name=payload.analyst_name,
            notes=payload.notes,
            status=payload.status,
        )
        return record
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/detection/gaps")
async def list_detection_gaps(
    campaign_id: Optional[str] = None,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Lists all verified detection gaps."""
    gaps = await DetectionVerificationService.get_detection_gaps(
        db=db,
        tenant_id=tenant_id,
        campaign_id=campaign_id,
    )
    return gaps
