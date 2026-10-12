import asyncio
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id, get_current_user
from backend.models.forensic_job import ForensicJob
from backend.services.velociraptor_service import (
    dispatch_collection,
    VelociraptorServiceError,
)

router = APIRouter()


class VelociraptorCollectRequest(BaseModel):
    client_id: str
    artifact_name: str
    custodian_name: str
    custodian_email: str
    parameters: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class ForensicCollectionResponse(BaseModel):
    collection_id: str
    tenant_id: str
    client_id: str
    artifact_name: str
    status: str
    evidence_id: Optional[str] = None
    sha256_hash: Optional[str] = None
    chain_of_custody_id: Optional[str] = None
    created_at: datetime
    external_job_id: Optional[str] = None
    job_id: Optional[str] = None


@router.post(
    "/collect",
    response_model=ForensicCollectionResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def dispatch_velociraptor_collection(
    payload: VelociraptorCollectRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Persist the job and report dispatch state without claiming evidence acquisition."""
    actor_id = current_user.get("user_id")
    authenticated_tenant = current_user.get("tenant_id")

    if not actor_id or not authenticated_tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user and tenant are required.",
        )

    if str(authenticated_tenant) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authenticated tenant does not match the requested tenant.",
        )

    now = datetime.utcnow()
    job = ForensicJob(
        tenant_id=str(tenant_id),
        actor_id=str(actor_id),
        target=payload.client_id,
        tool="VELOCIRAPTOR",
        operation="COLLECTION",
        artifact_name=payload.artifact_name,
        status="QUEUED",
        parameters={
            **(payload.parameters or {}),
            "custodian_name": payload.custodian_name,
            "custodian_email": payload.custodian_email,
            "notes": payload.notes,
        },
        created_at=now,
        updated_at=now,
    )

    db.add(job)
    try:
        await db.commit()
        await db.refresh(job)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not persist the forensic job.",
        ) from exc

    try:
        flow_id = await asyncio.to_thread(
            dispatch_collection,
            payload.client_id,
            payload.artifact_name,
            payload.parameters,
        )
    except VelociraptorServiceError as exc:
        job.status = "FAILED"
        job.error_message = str(exc)
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        try:
            await db.commit()
        except Exception:
            await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    job.external_job_id = str(flow_id)
    job.status = "RUNNING"
    job.started_at = datetime.utcnow()
    job.updated_at = datetime.utcnow()

    try:
        await db.commit()
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Collection was dispatched, but its external job ID could not "
                "be persisted. Check Velociraptor before retrying."
            ),
        ) from exc

    return ForensicCollectionResponse(
        collection_id=str(flow_id),
        tenant_id=str(tenant_id),
        client_id=payload.client_id,
        artifact_name=payload.artifact_name,
        status="DISPATCHED",
        evidence_id=None,
        sha256_hash=None,
        chain_of_custody_id=None,
        created_at=job.created_at,
        external_job_id=str(flow_id),
        job_id=str(job.job_id),
    )



class ForensicJobStatusResponse(BaseModel):
    job_id: str
    tenant_id: str
    case_id: Optional[str] = None
    target: str
    tool: str
    operation: str
    artifact_name: Optional[str] = None
    status: str
    external_job_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime


@router.get(
    "/jobs/{job_id}",
    response_model=ForensicJobStatusResponse,
)
async def get_forensic_job_status(
    job_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return a job belonging to the authenticated tenant."""
    authenticated_tenant = current_user.get("tenant_id")
    if not authenticated_tenant or str(authenticated_tenant) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authenticated tenant does not match the requested tenant.",
        )

    result = await db.execute(
        select(ForensicJob).where(
            ForensicJob.job_id == job_id,
            ForensicJob.tenant_id == str(tenant_id),
        )
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forensic job not found.",
        )

    return ForensicJobStatusResponse(
        job_id=str(job.job_id),
        tenant_id=str(job.tenant_id),
        case_id=job.case_id,
        target=job.target,
        tool=job.tool,
        operation=job.operation,
        artifact_name=job.artifact_name,
        status=job.status,
        external_job_id=job.external_job_id,
        error_message=job.error_message,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        updated_at=job.updated_at,
    )
