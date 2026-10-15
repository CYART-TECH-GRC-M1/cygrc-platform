
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.audit.pdf_export import generate_audit_pdf
from backend.audit.service import (
    AuditNotFoundError,
    get_audit_for_export,
)

router = APIRouter(prefix="/api/v1/audits", tags=["Audit Export"])


@router.post("/{audit_id}/export")
def export_audit_pdf(audit_id: str):
    if not audit_id.strip():
        raise HTTPException(
            status_code=400,
            detail="Audit ID must not be empty",
        )

    try:
        audit = get_audit_for_export(audit_id)
    except AuditNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Audit not found",
        )

    try:
        pdf_bytes = generate_audit_pdf(audit)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Audit cannot be exported: {exc}",
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="PDF generation failed",
        )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="audit-{audit_id}.pdf"'
            )
        },
    )