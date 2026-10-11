import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.audit import AuditLog

logger = logging.getLogger("cygrc.audit")

SENSITIVE_FIELD_NAMES = {
    "password",
    "hashed_password",
    "secret",
    "client_secret",
    "token",
    "access_token",
    "refresh_token",
    "signoff_approval_token",
    "custodian_signature",
    "api_key",
    "private_key",
    "authorization",
}


def redact_sensitive_data(data: Any) -> Any:
    """Recursively redacts secrets and sensitive forensic payloads from audit data."""
    if isinstance(data, dict):
        redacted = {}
        for k, v in data.items():
            if str(k).lower() in SENSITIVE_FIELD_NAMES or any(
                secret_word in str(k).lower() for secret_word in ["password", "secret", "token", "signature"]
            ):
                redacted[k] = "[REDACTED]"
            else:
                redacted[k] = redact_sensitive_data(v)
        return redacted
    elif isinstance(data, list):
        return [redact_sensitive_data(item) for item in data]
    return data


async def record_audit_log(
    action: str,
    tenant_id: str,
    actor_id: Optional[str] = None,
    actor_email: Optional[str] = None,
    actor_role: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    result: str = "SUCCESS",
    correlation_id: Optional[str] = None,
    approval_reference: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    db: Optional[AsyncSession] = None,
) -> Dict[str, Any]:
    """
    Standardized security audit logging helper for Module 2.
    Ensures secrets are scrubbed and outputs audit trail to structured logging & persistence.
    """
    cid = correlation_id or f"corr-{uuid.uuid4().hex[:12]}"
    clean_details = redact_sensitive_data(details or {})

    audit_entry = {
        "log_id": str(uuid.uuid4()),
        "tenant_id": str(tenant_id),
        "actor_id": str(actor_id) if actor_id else None,
        "actor_email": actor_email,
        "actor_role": actor_role,
        "action": action,
        "resource_type": resource_type,
        "resource_id": str(resource_id) if resource_id else None,
        "result": result.upper(),
        "correlation_id": cid,
        "approval_reference": approval_reference,
        "details": clean_details,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Structured log line
    logger.info("AUDIT_EVENT: %s", json.dumps(audit_entry))

    # Persist to database if active DB session is available
    if db is not None:
        try:
            log_record = AuditLog(
                log_id=audit_entry["log_id"],
                tenant_id=audit_entry["tenant_id"],
                actor_id=audit_entry["actor_id"],
                actor_email=audit_entry["actor_email"],
                actor_role=audit_entry["actor_role"],
                action=audit_entry["action"],
                resource_type=audit_entry["resource_type"],
                resource_id=audit_entry["resource_id"],
                result=audit_entry["result"],
                correlation_id=audit_entry["correlation_id"],
                approval_reference=audit_entry["approval_reference"],
                details=clean_details,
                created_at=datetime.now(timezone.utc),
            )
            db.add(log_record)
            await db.flush()
        except Exception as e:
            logger.warning("Failed to persist audit log record to database: %s", e)
            try:
                db.expunge(log_record)
            except Exception:
                pass

    return audit_entry
