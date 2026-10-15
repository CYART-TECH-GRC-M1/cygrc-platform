from io import BytesIO
from pypdf import PdfReader
from backend.audit.pdf_export import generate_audit_pdf


def sample_audit():
    return {
        "audit_id": "AUD-001",
        "title": "Security Compliance Audit",
        "organization": "Example Organization",
        "executive_summary": "Review of supplied security controls.",
        "controls": [
            {
                "control_id": "AC-01",
                "title": "Access Control",
                "status": "Reviewed",
                "notes": "Evidence reviewed.",
            }
        ],
        "evidence": [
            {
                "name": "access-policy.pdf",
                "sha256": "abc123-test-hash",
            }
        ],
        "findings": [
            {
                "description": "Review access policy updates.",
                "severity": "Low",
                "status": "Open",
            }
        ],
        "sign_off": {
            "approved_by": "Reviewer Name",
            "role": "Auditor",
            "date": "2026-10-15",
            "status": "Pending",
            "review_reference": "REV-001",
        },
    }


def test_generates_valid_pdf_bytes():
    pdf = generate_audit_pdf(sample_audit())

    assert pdf.startswith(b"%PDF-")
    assert len(pdf) > 500


def test_rejects_missing_audit_id():
    audit = sample_audit()
    del audit["audit_id"]

    try:
        generate_audit_pdf(audit)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Audit ID" in str(exc)


def test_rejects_empty_audit():
    try:
        generate_audit_pdf({"audit_id": "AUD-002"})
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "empty" in str(exc).lower()


def test_rejects_non_dictionary_input():
    try:
        generate_audit_pdf(None)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "dictionary" in str(exc).lower()

def test_pdf_contains_required_sections_and_original_hash():
    pdf_bytes = generate_audit_pdf(sample_audit())
    reader = PdfReader(BytesIO(pdf_bytes))

    pdf_text = "\n".join(
        page.extract_text() or "" for page in reader.pages
    )

    assert "Executive Summary" in pdf_text
    assert "Control Matrix" in pdf_text
    assert "Evidence" in pdf_text
    assert "SHA-256" in pdf_text
    assert "Audit Sign-Off" in pdf_text
    assert "abc123-test-hash" in pdf_text
    assert "Reviewer Name" in pdf_text
    assert "REV-001" in pdf_text
