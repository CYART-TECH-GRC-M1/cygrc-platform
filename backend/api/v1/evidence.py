import hashlib
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.models.control import Control
from backend.models.evidence import Evidence, EvidenceFile, EvidenceReview
from backend.models.user import User
from backend.schemas.evidence import (
    EvidenceCreate,
    EvidenceDetailResponse,
    EvidenceFileUploadResponse,
    EvidenceResponse,
    EvidenceReviewCreate,
    EvidenceReviewResponse,
    EvidenceUpdate,
)

UPLOAD_DIR = Path(os.getenv("EVIDENCE_UPLOAD_DIR", "uploads/evidence")).resolve()
MAX_UPLOAD_BYTES = int(os.getenv("EVIDENCE_MAX_UPLOAD_MB", "20")) * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt", ".csv", ".docx", ".xlsx", ".log"}

router = APIRouter()


def _uuid_claim(user: Dict[str, Any], key: str) -> UUID:
    try:
        return UUID(str(user.get(key)))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token has a missing or invalid '{key}' claim.",
        )


async def _get_owned_evidence(
    db: AsyncSession, evidence_id: UUID, tenant_id: UUID
) -> Evidence:
    result = await db.execute(
        select(Evidence)
        .options(selectinload(Evidence.files), selectinload(Evidence.reviews))
        .where(Evidence.evidence_id == evidence_id, Evidence.tenant_id == tenant_id)
    )
    evidence = result.scalars().first()
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found."
        )
    return evidence


async def _require_tenant_user(db: AsyncSession, user_id: UUID, tenant_id: UUID) -> None:
    found = await db.execute(
        select(User.user_id).where(User.user_id == user_id, User.tenant_id == tenant_id)
    )
    if not found.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authenticated user does not exist in this tenant.",
        )


@router.post("/", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def create_evidence(
    payload: EvidenceCreate,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = _uuid_claim(user, "tenant_id")
    user_id = _uuid_claim(user, "user_id")

    control = await db.execute(
        select(Control.control_id).where(Control.control_id == payload.control_id)
    )
    if not control.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Control not found."
        )
    await _require_tenant_user(db, user_id, tenant_id)

    evidence = Evidence(
        tenant_id=tenant_id,
        control_id=payload.control_id,
        uploaded_by=user_id,
        title=payload.title,
        description=payload.description,
    )
    db.add(evidence)
    await db.commit()
    await db.refresh(evidence)
    return evidence


@router.get("/", response_model=List[EvidenceResponse])
async def list_evidence(
    control_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = _uuid_claim(user, "tenant_id")
    query = select(Evidence).where(Evidence.tenant_id == tenant_id)
    if control_id:
        query = query.where(Evidence.control_id == control_id)
    query = query.order_by(Evidence.uploaded_at.desc()).offset(skip).limit(min(limit, 500))
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{evidence_id}", response_model=EvidenceDetailResponse)
async def get_evidence(
    evidence_id: UUID,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _get_owned_evidence(db, evidence_id, _uuid_claim(user, "tenant_id"))


@router.put("/{evidence_id}", response_model=EvidenceResponse)
async def update_evidence(
    evidence_id: UUID,
    payload: EvidenceUpdate,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    evidence = await _get_owned_evidence(db, evidence_id, _uuid_claim(user, "tenant_id"))
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(evidence, field, value)
    await db.commit()
    await db.refresh(evidence)
    return evidence


@router.delete("/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evidence(
    evidence_id: UUID,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    evidence = await _get_owned_evidence(db, evidence_id, _uuid_claim(user, "tenant_id"))
    await db.delete(evidence)
    await db.commit()
    return None


@router.post(
    "/{evidence_id}/files",
    response_model=EvidenceFileUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_evidence_file(
    evidence_id: UUID,
    file: UploadFile = File(...),
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = _uuid_claim(user, "tenant_id")
    evidence = await _get_owned_evidence(db, evidence_id, tenant_id)

    original_name = Path(file.filename or "").name
    ext = Path(original_name).suffix.lower()
    if not original_name or ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", original_name)[:200]
    target_dir = UPLOAD_DIR / str(tenant_id) / str(evidence.evidence_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{uuid4().hex}_{safe_name}"

    sha = hashlib.sha256()
    size = 0
    try:
        with open(target, "wb") as out:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit.",
                    )
                sha.update(chunk)
                out.write(chunk)
    except Exception:
        target.unlink(missing_ok=True)
        raise

    record = EvidenceFile(
        evidence_id=evidence.evidence_id,
        file_name=original_name,
        file_path=str(target),
        file_size=size,
        file_type=file.content_type,
    )
    db.add(record)
    try:
        await db.commit()
    except Exception:
        target.unlink(missing_ok=True)
        raise
    await db.refresh(record)

    return EvidenceFileUploadResponse(
        file_id=record.file_id,
        evidence_id=record.evidence_id,
        file_name=record.file_name,
        file_size=record.file_size,
        file_type=record.file_type,
        uploaded_at=record.uploaded_at,
        sha256=sha.hexdigest(),
    )


@router.get("/{evidence_id}/files/{file_id}/download")
async def download_evidence_file(
    evidence_id: UUID,
    file_id: UUID,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    evidence = await _get_owned_evidence(db, evidence_id, _uuid_claim(user, "tenant_id"))
    record = next((f for f in evidence.files if f.file_id == file_id), None)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")

    path = Path(record.file_path).resolve()
    if UPLOAD_DIR not in path.parents or not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not available.")
    return FileResponse(path, filename=record.file_name)


@router.post(
    "/{evidence_id}/reviews",
    response_model=EvidenceReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def review_evidence(
    evidence_id: UUID,
    payload: EvidenceReviewCreate,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = _uuid_claim(user, "tenant_id")
    reviewer_id = _uuid_claim(user, "user_id")
    evidence = await _get_owned_evidence(db, evidence_id, tenant_id)
    await _require_tenant_user(db, reviewer_id, tenant_id)

    review = EvidenceReview(
        evidence_id=evidence.evidence_id,
        reviewer_id=reviewer_id,
        review_status=payload.review_status,
        comments=payload.comments,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


@router.get("/{evidence_id}/reviews", response_model=List[EvidenceReviewResponse])
async def list_evidence_reviews(
    evidence_id: UUID,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    evidence = await _get_owned_evidence(db, evidence_id, _uuid_claim(user, "tenant_id"))
    return evidence.reviews
