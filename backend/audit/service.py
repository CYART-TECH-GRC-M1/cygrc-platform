
from typing import Any


class AuditNotFoundError(Exception):
    """Raised when an audit does not exist."""


class AuditDataError(Exception):
    """Raised when an audit has no usable export data."""


# Temporary in-memory store for endpoint development and tests.
# Replace this with the project's database service when it is implemented.
_AUDITS: dict[str, dict[str, Any]] = {}


def get_audit_for_export(audit_id: str) -> dict[str, Any]:
    audit = _AUDITS.get(audit_id)

    if audit is None:
        raise AuditNotFoundError(audit_id)

    return audit


def register_audit_for_testing(audit: dict[str, Any]) -> None:
    """Register sample data for endpoint tests only."""
    audit_id = audit.get("audit_id")

    if not audit_id:
        raise ValueError("Audit must contain an audit_id")

    _AUDITS[audit_id] = audit


def clear_test_audits() -> None:
    """Clear temporary in-memory audit data."""
    _AUDITS.clear()
