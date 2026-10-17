import asyncio
import hashlib
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.models.control import Control
from backend.models.evidence import Evidence, EvidenceRequirement
from backend.models.user import User
from backend.models.tenant_control import TenantControlMapping
from backend.schemas.evidence import (
    EvidenceDetailResponse,
    EvidenceUploadResponse,
    EvidenceVerifyResponse,
)

S3_BUCKET = os.getenv("EVIDENCE_S3_BUCKET")
LOCAL_DIR = Path(os.getenv("EVIDENCE_UPLOAD_DIR", "uploads/evidence")).resolve()
MAX_UPLOAD_BYTES = int(os.getenv("EVIDENCE_MAX_UPLOAD_MB", "20")) * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt", ".csv", ".docx", ".xlsx", ".log", ".json"}

router = APIRouter()


def _uuid_claim(user: Dict[str, Any], key: str) -> UUID:
    try:
        return UUID(str(user.get(key)))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token has a missing or invalid '{key}' claim.",
        )


async def _store_blob(tmp_path: str, key: str) -> None:
    if S3_BUCKET:
        import boto3

        await asyncio.to_thread(boto3.client("s3").upload_file, tmp_path, S3_BUCKET, key)
    else:
        dest = LOCAL_DIR / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(shutil.copyfile, tmp_path, dest)


def _hash_blob_sync(key: str) -> str:
    sha = hashlib.sha256()
    if S3_BUCKET:
        import boto3

        body = boto3.client("s3").get_object(Bucket=S3_BUCKET, Key=key)["Body"]
        for chunk in body.iter_chunks(1024 * 1024):
            sha.update(chunk)
    else:
        path = (LOCAL_DIR / key).resolve()
        if LOCAL_DIR not in path.parents or not path.is_file():
            raise FileNotFoundError(key)
        with open(path, "rb") as f:
            while chunk := f.read(1024 * 1024):
                sha.update(chunk)
    return sha.hexdigest()


async def _get_owned_evidence(db: AsyncSession, evidence_id: UUID, tenant_id: UUID) -> Evidence:
    result = await db.execute(
        select(Evidence).where(Evidence.evidence_id == evidence_id, Evidence.tenant_id == tenant_id)
    )
    evidence = result.scalars().first()
    if not evidence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found.")
    return evidence


@router.post("/", response_model=EvidenceUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    control_id: UUID = Form(...),
    title: str = Form(..., min_length=1, max_length=255),
    description: Optional[str] = Form(None),
    requirement_id: Optional[UUID] = Form(None),
    file: UploadFile = File(...),
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = _uuid_claim(user, "tenant_id")
    user_id = _uuid_claim(user, "user_id")

    original_name = Path(file.filename or "").name
    if not original_name or Path(original_name).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    control_mapping = await db.execute(
        select(TenantControlMapping.mapping_id).where(
            TenantControlMapping.tenant_id == tenant_id,
            TenantControlMapping.control_id == control_id,
            TenantControlMapping.status == "ACTIVE",
        )
    )

    if not control_mapping.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found for this tenant.",
        )

    if requirement_id:
        req = await db.execute(
            select(EvidenceRequirement.requirement_id).where(
                EvidenceRequirement.requirement_id == requirement_id,
                EvidenceRequirement.tenant_id == tenant_id,
                EvidenceRequirement.control_id == control_id,
            )
        )
        if not req.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirement not found for this control.",
            )

    uploader = await db.execute(
        select(User.user_id).where(User.user_id == user_id, User.tenant_id == tenant_id)
    )
    if not uploader.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authenticated user does not exist in this tenant.",
        )

    # Stream to a temp file while hashing and enforcing the size limit.
    sha = hashlib.sha256()
    size = 0
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name
        try:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit.",
                    )
                sha.update(chunk)
                tmp.write(chunk)
        except Exception:
            os.unlink(tmp_path)
            raise

    evidence_id = uuid4()
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", original_name)[:200]
    key = f"{tenant_id}/{evidence_id}/{safe_name}"

    try:
        await _store_blob(tmp_path, key)
    finally:
        os.unlink(tmp_path)

    evidence = Evidence(
        evidence_id=evidence_id,
        tenant_id=tenant_id,
        control_id=control_id,
        requirement_id=requirement_id,
        uploaded_by=user_id,
        title=title,
        description=description,
        blob_s3_key=key,
        sha256=sha.hexdigest(),
        file_name=original_name,
        file_size=size,
        content_type=file.content_type,
    )
    db.add(evidence)
    try:
        await db.commit()
    except Exception:
        if not S3_BUCKET:
            (LOCAL_DIR / key).unlink(missing_ok=True)
        raise
    await db.refresh(evidence)
    return evidence


@router.get("/", response_model=List[EvidenceDetailResponse])
async def list_evidence(
    control_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = _uuid_claim(user, "tenant_id")
    query = select(Evidence).where(Evidence.tenant_id == tenant_id)
    if control_id:
        query = query.where(Evidence.control_id == control_id)
    query = query.order_by(Evidence.uploaded_at.desc()).offset(skip).limit(limit)
    return (await db.execute(query)).scalars().all()


@router.get("/{evidence_id}", response_model=EvidenceDetailResponse)
async def get_evidence(
    evidence_id: UUID,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _get_owned_evidence(db, evidence_id, _uuid_claim(user, "tenant_id"))


@router.get("/{evidence_id}/verify", response_model=EvidenceVerifyResponse)
async def verify_evidence(
    evidence_id: UUID,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Re-hash the stored blob and compare with the SHA-256 recorded at upload."""
    evidence = await _get_owned_evidence(db, evidence_id, _uuid_claim(user, "tenant_id"))
    if not evidence.blob_s3_key or not evidence.sha256:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence has no stored file.")
    try:
        computed = await asyncio.to_thread(_hash_blob_sync, evidence.blob_s3_key)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not available.")
    return EvidenceVerifyResponse(
        evidence_id=evidence.evidence_id,
        stored_sha256=evidence.sha256,
        computed_sha256=computed,
        intact=(computed == evidence.sha256),
    )
