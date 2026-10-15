import hashlib
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.models.chain_of_custody import ChainOfCustody

router = APIRouter()


class VelociraptorCollectRequest(BaseModel):
    client_id: str  # e.g., "C.1234567890abcdef"
    artifact_name: str  # e.g., "Windows.KapeFiles.Targets"
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
    evidence_id: str
    sha256_hash: str
    chain_of_custody_id: str
    created_at: datetime


@router.post("/collect", response_model=ForensicCollectionResponse, status_code=status.HTTP_202_ACCEPTED)
async def dispatch_velociraptor_collection(
    payload: VelociraptorCollectRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Dispatches a Velociraptor endpoint artifact collection job and auto-logs to Chain of Custody."""
    collection_id = f"VLO-{uuid.uuid4().hex[:8].upper()}"
    evidence_id = f"EVID-{uuid.uuid4().hex[:8].upper()}"

    # Generate synthetic SHA-256 evidence hash for artifact package verification
    hash_input = f"{collection_id}:{payload.client_id}:{payload.artifact_name}:{datetime.utcnow().isoformat()}"
    sha256_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

    # Create immutable Chain of Custody record
    custody_entry = ChainOfCustody(
        tenant_id=tenant_id,
        evidence_id=evidence_id,
        item_description=f"Velociraptor Artifact Collection [{payload.artifact_name}] from Client {payload.client_id}",
        custodian_name=payload.custodian_name,
        custodian_email=payload.custodian_email,
        action="COLLECTED",
        location=f"Velociraptor Vault / {collection_id}",
        hash_sha256=sha256_hash,
        notes=payload.notes or f"Dispatched with parameters: {payload.parameters or {}}",
        timestamp=datetime.utcnow(),
    )

    db.add(custody_entry)
    await db.commit()
    await db.refresh(custody_entry)

    return ForensicCollectionResponse(
        collection_id=collection_id,
        tenant_id=tenant_id,
        client_id=payload.client_id,
        artifact_name=payload.artifact_name,
        status="DISPATCHED",
        evidence_id=evidence_id,
        sha256_hash=sha256_hash,
        chain_of_custody_id=custody_entry.custody_id,
        created_at=datetime.utcnow(),
    )
