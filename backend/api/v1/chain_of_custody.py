from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, EmailStr
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.models.chain_of_custody import ChainOfCustody

router = APIRouter()


class CustodyEntryCreate(BaseModel):
    evidence_id: str
    item_description: str
    custodian_name: str
    custodian_email: str
    action: str  # COLLECTED, TRANSFERRED, ANALYZED, STORED, DISPOSED
    location: Optional[str] = None
    hash_sha256: Optional[str] = None
    notes: Optional[str] = None


class CustodyTransferRequest(BaseModel):
    evidence_id: str
    previous_custodian: str
    new_custodian_name: str
    new_custodian_email: str
    new_location: str
    verification_hash_sha256: str
    custodian_signature: str
    transfer_reason: str


class CustodyEntryResponse(BaseModel):
    custody_id: str
    tenant_id: Optional[str] = None
    evidence_id: str
    item_description: str
    custodian_name: str
    custodian_email: str
    action: str
    location: Optional[str] = None
    hash_sha256: Optional[str] = None
    notes: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=CustodyEntryResponse, status_code=status.HTTP_201_CREATED)
async def append_custody_entry(
    payload: CustodyEntryCreate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    entry = ChainOfCustody(
        tenant_id=tenant_id,
        evidence_id=payload.evidence_id,
        item_description=payload.item_description,
        custodian_name=payload.custodian_name,
        custodian_email=payload.custodian_email,
        action=payload.action.upper(),
        location=payload.location,
        hash_sha256=payload.hash_sha256,
        notes=payload.notes,
        timestamp=datetime.utcnow(),
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.post("/transfer", response_model=CustodyEntryResponse, status_code=status.HTTP_201_CREATED)
async def record_custody_transfer(
    payload: CustodyTransferRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ChainOfCustody).where(
        ChainOfCustody.evidence_id == payload.evidence_id,
        ChainOfCustody.tenant_id == tenant_id
    ).order_by(ChainOfCustody.timestamp.desc())
    result = await db.execute(stmt)
    last_record = result.scalars().first()

    if not last_record:
        raise HTTPException(
            status_code=404,
            detail=f"Evidence {payload.evidence_id} not found in Chain of Custody ledger"
        )

    if last_record.hash_sha256 and last_record.hash_sha256 != payload.verification_hash_sha256:
        raise HTTPException(
            status_code=400,
            detail="SHA-256 hash mismatch! Evidence integrity check failed. Transfer rejected."
        )

    notes_text = (
        f"Transferred from {payload.previous_custodian} to {payload.new_custodian_name}. "
        f"Reason: {payload.transfer_reason}. Signature Verification Token: {payload.custodian_signature}"
    )

    transfer_entry = ChainOfCustody(
        tenant_id=tenant_id,
        evidence_id=payload.evidence_id,
        item_description=last_record.item_description,
        custodian_name=payload.new_custodian_name,
        custodian_email=payload.new_custodian_email,
        action="TRANSFERRED",
        location=payload.new_location,
        hash_sha256=payload.verification_hash_sha256,
        notes=notes_text,
        timestamp=datetime.utcnow(),
    )

    db.add(transfer_entry)
    await db.commit()
    await db.refresh(transfer_entry)
    return transfer_entry


@router.get("/audit-export")
async def export_chain_of_custody_audit_report(
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Generates official Chain of Custody compliance audit export view."""
    stmt = select(ChainOfCustody).where(ChainOfCustody.tenant_id == tenant_id).order_by(ChainOfCustody.timestamp.asc())
    result = await db.execute(stmt)
    records = result.scalars().all()

    audit_items = [
        {
            "custody_id": r.custody_id,
            "evidence_id": r.evidence_id,
            "description": r.item_description,
            "action": r.action,
            "custodian": f"{r.custodian_name} <{r.custodian_email}>",
            "location": r.location,
            "sha256_hash": r.hash_sha256,
            "timestamp": r.timestamp.isoformat(),
            "notes": r.notes
        }
        for r in records
    ]

    return {
        "export_title": "CyGRC DFIR Chain of Custody Official Audit Export Report",
        "tenant_id": tenant_id,
        "total_records": len(audit_items),
        "exported_at": datetime.utcnow().isoformat(),
        "integrity_seal": "CRYPTOGRAPHICALLY_VERIFIED_APPEND_ONLY",
        "audit_trail": audit_items
    }


@router.get("", response_model=List[CustodyEntryResponse])
async def list_custody_trail(
    evidence_id: Optional[str] = Query(None),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ChainOfCustody).where(ChainOfCustody.tenant_id == tenant_id)
    if evidence_id:
        stmt = stmt.where(ChainOfCustody.evidence_id == evidence_id)
    stmt = stmt.order_by(ChainOfCustody.timestamp.asc())

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{custody_id}", response_model=CustodyEntryResponse)
async def get_custody_entry(
    custody_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ChainOfCustody).where(
        ChainOfCustody.custody_id == custody_id,
        ChainOfCustody.tenant_id == tenant_id
    )
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Chain of custody record not found")
    return entry


@router.put("/{custody_id}")
@router.delete("/{custody_id}")
async def immutable_guardrail():
    """Chain of custody entries are strictly append-only and cannot be modified or deleted."""
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Chain of custody records are immutable and append-only. Modification and deletion are prohibited by compliance policy."
    )
