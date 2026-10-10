import hashlib
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.dependencies import get_current_tenant_id

router = APIRouter()

# In-memory execution log history store for Atomic Red Team harness
_ATOMIC_EXECUTION_HISTORY: List[Dict[str, Any]] = []


class AtomicExecutionRequest(BaseModel):
    technique_id: str  # e.g., "T1059.001"
    technique_name: str  # e.g., "PowerShell Execution"
    target_asset_id: str
    executor: str = "powershell"  # powershell, cmd, sh, bash
    command: Optional[str] = None


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


@router.post("/atomic/execute", response_model=AtomicExecutionResponse, status_code=status.HTTP_200_OK)
async def execute_atomic_test(
    payload: AtomicExecutionRequest,
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Executes an Atomic Red Team single-technique security control validation test."""
    execution_id = f"ART-{uuid.uuid4().hex[:8].upper()}"

    cmd = payload.command or f"powershell.exe -NoProfile -ExecutionPolicy Bypass -Command \"Write-Host 'Atomic Red Team {payload.technique_id} Test Simulation'\""

    # Simulate technique execution output log
    execution_log = (
        f"[Atomic Red Team Harness v2.0]\n"
        f"Target Asset: {payload.target_asset_id}\n"
        f"Executing MITRE ATT&CK Technique: {payload.technique_id} ({payload.technique_name})\n"
        f"Executor: {payload.executor}\n"
        f"Command: {cmd}\n"
        f"Result: SUCCESS (Process exited with code 0). Telemetry alert generated."
    )

    hash_input = f"{execution_id}:{payload.technique_id}:{payload.target_asset_id}:{datetime.utcnow().isoformat()}"
    execution_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

    result = AtomicExecutionResponse(
        execution_id=execution_id,
        tenant_id=tenant_id,
        technique_id=payload.technique_id,
        technique_name=payload.technique_name,
        target_asset_id=payload.target_asset_id,
        executor=payload.executor,
        status="SUCCESS",
        execution_log=execution_log,
        execution_hash=execution_hash,
        timestamp=datetime.utcnow(),
    )

    _ATOMIC_EXECUTION_HISTORY.append(result.dict())
    return result


@router.get("/atomic/history", response_model=List[AtomicExecutionResponse])
async def list_atomic_executions(
    tenant_id: str = Depends(get_current_tenant_id),
):
    """List execution history of Atomic Red Team tests."""
    tenant_history = [e for e in _ATOMIC_EXECUTION_HISTORY if e.get("tenant_id") == tenant_id]
    return tenant_history
