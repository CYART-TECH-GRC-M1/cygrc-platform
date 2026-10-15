from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.main import app
from backend.audit.service import (
    register_audit_for_testing,
    clear_test_audits,
)

client = TestClient(app)


def setup_function():
    clear_test_audits()


def teardown_function():
    clear_test_audits()


def sample_audit():
    return {
        "audit_id": "AUD-101",
        "title": "Security Compliance Audit",
        "organization": "Example Organization",
        "executive_summary": "Security controls were reviewed.",
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
        "sign_off": {
            "approved_by": "Reviewer",
            "role": "Auditor",
            "date": "2026-10-15",
            "status": "Pending",
            "review_reference": "REV-101",
        },
    }


def test_export_returns_pdf():
    register_audit_for_testing(sample_audit())

    response = client.post("/api/v1/audits/AUD-101/export")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-")
    assert "attachment" in response.headers["content-disposition"]


def test_export_unknown_audit_returns_404():
    response = client.post("/api/v1/audits/UNKNOWN/export")

    assert response.status_code == 404
    assert response.json()["detail"] == "Audit not found"
def test_export_invalid_audit_data_returns_422():
    register_audit_for_testing({"audit_id": "AUD-BAD"})

    response = client.post("/api/v1/audits/AUD-BAD/export")

    assert response.status_code == 422
    assert "cannot be exported" in response.json()["detail"]


def test_export_pdf_generation_failure_returns_500():
    register_audit_for_testing(sample_audit())

    with patch(
        "backend.audit.routes.generate_audit_pdf",
        side_effect=RuntimeError("Simulated PDF failure"),
    ):
        response = client.post("/api/v1/audits/AUD-101/export")

    assert response.status_code == 500
    assert response.json()["detail"] == "PDF generation failed"
