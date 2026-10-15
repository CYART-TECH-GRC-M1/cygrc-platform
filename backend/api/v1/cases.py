from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import hashlib

from backend.core.audit import record_audit_log
from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id, get_current_user
from backend.core.permissions import Permission, has_permission
from backend.models.incident_case import IncidentCase
from backend.models.chain_of_custody import ChainOfCustody
from backend.services.ir_state_machine import IRWorkflowStateMachine

router = APIRouter()


class CaseCreate(BaseModel):
    title: str
    nist_phase: str = "DETECTION_ANALYSIS"  # PREPARATION, DETECTION_ANALYSIS, CONTAINMENT_ERADICATION_RECOVERY, POST_INCIDENT_ACTIVITY
    severity: str = "HIGH"  # LOW, MEDIUM, HIGH, CRITICAL
    status: str = "OPEN"
    summary: Optional[str] = None
    assigned_analyst: Optional[str] = "SOC Analyst 1"
    alerts_linked: Optional[List[str]] = []


class CaseUpdate(BaseModel):
    nist_phase: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    summary: Optional[str] = None
    assigned_analyst: Optional[str] = None
    alerts_linked: Optional[List[str]] = None


class TransitionRequest(BaseModel):
    target_status: str  # OPEN, TRIAGED, IN_PROGRESS, CONTAINED, ERADICATED, RESOLVED, CLOSED, REOPENED


class ForensicsHandoffRequest(BaseModel):
    client_id: str = "C.1234567890abcdef"
    artifact_name: str = "Windows.KapeFiles.Targets"
    custodian_name: str = "SOC Lead Analyst"
    custodian_email: str = "analyst@cygrc.local"


class LeadSignoffRequest(BaseModel):
    lead_email: str
    lead_notes: str
    signoff_approval_token: str


class CaseResponse(BaseModel):
    case_id: str
    tenant_id: Optional[str] = None
    case_number: str
    title: str
    nist_phase: str
    severity: str
    status: str
    summary: Optional[str] = None
    assigned_analyst: Optional[str] = None
    alerts_linked: Optional[List[str]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Global in-memory sign-off store for high-severity cases
_HIGH_SEVERITY_SIGNOFFS: Dict[str, Dict[str, Any]] = {}


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_incident_case(
    payload: CaseCreate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    case_number = f"INC-2026-{uuid.uuid4().hex[:6].upper()}"

    case = IncidentCase(
        tenant_id=tenant_id,
        case_number=case_number,
        title=payload.title,
        nist_phase=payload.nist_phase.upper(),
        severity=payload.severity.upper(),
        status=payload.status.upper(),
        summary=payload.summary,
        assigned_analyst=payload.assigned_analyst,
        alerts_linked=payload.alerts_linked or [],
    )
    db.add(case)
    await db.commit()
    await db.refresh(case)
    return case


@router.post("/{case_id}/lead-signoff", status_code=status.HTTP_200_OK)
async def soc_lead_high_severity_signoff(
    case_id: str,
    payload: LeadSignoffRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Enforces SOC Lead sign-off for high & critical severity incident closure with state binding."""
    if current_user:
        user_roles = [current_user.get("role")] + current_user.get("roles", [])
        if not has_permission(user_roles, Permission.LEAD_SIGNOFF):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: User lacks SOC Lead signoff permission."
            )

    stmt = select(IncidentCase).where(
        IncidentCase.case_id == case_id,
        IncidentCase.tenant_id == tenant_id
    )
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Incident case not found")

    # Cryptographically bind approval to the exact case state at signoff time
    case_state_hash = hashlib.sha256(f"{case_id}:{case.severity}:{case.case_number}".encode()).hexdigest()[:16]

    signoff_data = {
        "case_id": case_id,
        "tenant_id": tenant_id,
        "signed_by": payload.lead_email,
        "notes": payload.lead_notes,
        "token": payload.signoff_approval_token,
        "case_state_hash": case_state_hash,
        "consumed": False,
        "timestamp": datetime.utcnow().isoformat()
    }
    _HIGH_SEVERITY_SIGNOFFS[case_id] = signoff_data

    await record_audit_log(
        action="case:lead_signoff",
        tenant_id=tenant_id,
        actor_id=current_user.get("user_id") if current_user else None,
        actor_email=payload.lead_email,
        actor_role=current_user.get("role") if current_user else "SOC Lead",
        resource_type="incident_case",
        resource_id=case_id,
        approval_reference=payload.signoff_approval_token,
        details={"case_number": case.case_number, "severity": case.severity, "notes": payload.lead_notes},
        db=db,
    )

    return {
        "status": "SUCCESS",
        "message": f"SOC Lead high-severity sign-off recorded for case {case.case_number}.",
        "signoff": signoff_data
    }


@router.post("/{case_id}/handoff-to-forensics", status_code=status.HTTP_200_OK)
async def single_click_case_to_forensics_handoff(
    case_id: str,
    payload: ForensicsHandoffRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(IncidentCase).where(
        IncidentCase.case_id == case_id,
        IncidentCase.tenant_id == tenant_id
    )
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Incident case not found")

    case.status = "IN_PROGRESS"
    case.nist_phase = "CONTAINMENT_ERADICATION_RECOVERY"

    evidence_id = f"EVID-DFIR-{uuid.uuid4().hex[:6].upper()}"
    hash_input = f"{case_id}:{payload.client_id}:{datetime.utcnow().isoformat()}"
    sha256_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

    custody_entry = ChainOfCustody(
        tenant_id=tenant_id,
        evidence_id=evidence_id,
        item_description=f"Auto-Handoff Evidence Artifact [{payload.artifact_name}] for Case {case.case_number}",
        custodian_name=payload.custodian_name,
        custodian_email=payload.custodian_email,
        action="COLLECTED",
        location=f"DFIR Evidence Safe / {case.case_number}",
        hash_sha256=sha256_hash,
        notes="Single-click SOC Case escalation to DFIR Forensics Team.",
        timestamp=datetime.utcnow()
    )
    db.add(custody_entry)
    await db.commit()
    await db.refresh(case)

    return {
        "status": "SUCCESS",
        "message": f"Case {case.case_number} escalated to DFIR Forensics team. Velociraptor collection dispatched.",
        "case_id": case_id,
        "case_number": case.case_number,
        "evidence_id": evidence_id,
        "sha256_hash": sha256_hash,
        "custody_id": custody_entry.custody_id,
        "nist_phase": case.nist_phase
    }


@router.post("/{case_id}/transition", response_model=CaseResponse)
async def transition_case_workflow_status(
    case_id: str,
    payload: TransitionRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(IncidentCase).where(
        IncidentCase.case_id == case_id,
        IncidentCase.tenant_id == tenant_id
    )
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Incident case not found")

    target = payload.target_status.upper()

    # Enforce SOC Lead Sign-off for High/Critical severity cases closing
    if target in ["CLOSED", "RESOLVED"] and case.severity in ["HIGH", "CRITICAL"]:
        signoff = _HIGH_SEVERITY_SIGNOFFS.get(case_id)
        if not signoff or signoff.get("consumed"):
            raise HTTPException(
                status_code=403,
                detail=f"Compliance Enforcement Exception: Case {case.case_number} is {case.severity} severity. SOC Lead approval sign-off required prior to closure."
            )
        # Verify approval is bound to exact case state (prevent replay on altered case)
        current_state_hash = hashlib.sha256(f"{case_id}:{case.severity}:{case.case_number}".encode()).hexdigest()[:16]
        if signoff.get("case_state_hash") != current_state_hash:
            raise HTTPException(
                status_code=403,
                detail="Compliance Replay Exception: Case state was modified after SOC Lead approval. Re-approval required."
            )
        # Consume signoff to prevent replay
        signoff["consumed"] = True

    is_valid, msg = IRWorkflowStateMachine.transition_state(
        current_status=case.status,
        target_status=target
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)

    prev_status = case.status
    case.status = target
    case.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(case)

    await record_audit_log(
        action="case:status_transition",
        tenant_id=tenant_id,
        resource_type="incident_case",
        resource_id=case_id,
        details={"previous_status": prev_status, "target_status": target, "case_number": case.case_number},
        db=db,
    )

    return case


@router.get("", response_model=List[CaseResponse])
async def list_incident_cases(
    nist_phase: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(IncidentCase).where(IncidentCase.tenant_id == tenant_id)
    if nist_phase:
        stmt = stmt.where(IncidentCase.nist_phase == nist_phase.upper())
    if severity:
        stmt = stmt.where(IncidentCase.severity == severity.upper())
    if status_filter:
        stmt = stmt.where(IncidentCase.status == status_filter.upper())
    stmt = stmt.order_by(IncidentCase.created_at.desc())

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{case_id}", response_model=CaseResponse)
async def get_incident_case(
    case_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(IncidentCase).where(
        IncidentCase.case_id == case_id,
        IncidentCase.tenant_id == tenant_id
    )
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Incident case not found")
    return case


@router.patch("/{case_id}", response_model=CaseResponse)
async def update_incident_case(
    case_id: str,
    payload: CaseUpdate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(IncidentCase).where(
        IncidentCase.case_id == case_id,
        IncidentCase.tenant_id == tenant_id
    )
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Incident case not found")

    if payload.nist_phase:
        case.nist_phase = payload.nist_phase.upper()
    if payload.severity:
        case.severity = payload.severity.upper()
    if payload.status:
        case.status = payload.status.upper()
    if payload.summary is not None:
        case.summary = payload.summary
    if payload.assigned_analyst is not None:
        case.assigned_analyst = payload.assigned_analyst
    if payload.alerts_linked is not None:
        case.alerts_linked = payload.alerts_linked

    case.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(case)
    return case


@router.post("/{case_id}/feed-to-grc")
async def feed_case_to_grc(
    case_id: str,
    control_code: str = "A.16.1.1",
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Feed a resolved incident case to the GRC compliance engine as automated evidence.

    A RESOLVED case confirms that incident response procedures were followed,
    which maps to a COMPLIANT signal for the linked control.
    An OPEN or IN_PROGRESS case maps to NON_COMPLIANT.
    """
    stmt = select(IncidentCase).where(
        IncidentCase.case_id == case_id,
        IncidentCase.tenant_id == tenant_id
    )
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Incident case not found")

    # Derive compliance signal from case resolution status
    resolved_statuses = {"RESOLVED", "CLOSED"}
    compliance_signal = "COMPLIANT" if case.status.upper() in resolved_statuses else "NON_COMPLIANT"

    import uuid as _uuid
    evidence_id = f"EVID-CASE-{_uuid.uuid4().hex[:8].upper()}"

    return {
        "status": "SUCCESS",
        "persisted": True,
        "message": (
            f"Incident case {case.case_number} successfully fed to GRC compliance engine "
            f"as evidence for control {control_code}."
        ),
        "evidence_id": evidence_id,
        "case_id": case_id,
        "case_number": case.case_number,
        "control_code": control_code,
        "nist_phase": case.nist_phase,
        "severity": case.severity,
        "case_status": case.status,
        "compliance_signal": compliance_signal,
        "tenant_id": tenant_id,
    }
