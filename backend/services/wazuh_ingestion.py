"""Wazuh SIEM alert webhook ingestion service.

Handles:
- Validation and normalization of Wazuh event payloads.
- Stable source event identifiers generation.
- Idempotent processing to prevent duplicate alerts.
- Durable persistence in database.
- Real-time alert publication to tenant stream.
- Structured failure logging.
"""
import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.alert import Alert, AlertSeverity, AlertStatus
from backend.services.alert_stream import AlertStreamBroker

logger = logging.getLogger(__name__)


class WazuhIngestionService:
    @staticmethod
    def calculate_source_event_id(raw_event: Dict[str, Any]) -> str:
        """Derives a stable, deterministic source event identifier for deduplication."""
        # Check standard Wazuh event ID fields
        if raw_event.get("id"):
            return str(raw_event["id"])
        if raw_event.get("_id"):
            return str(raw_event["_id"])

        rule = raw_event.get("rule", {})
        agent = raw_event.get("agent", {})
        rule_id = str(rule.get("id", ""))
        agent_id = str(agent.get("id", agent.get("name", "unknown")))
        timestamp = str(raw_event.get("timestamp") or raw_event.get("@timestamp", ""))
        full_log = str(raw_event.get("full_log") or rule.get("description", ""))

        raw_id_str = f"{agent_id}:{rule_id}:{timestamp}:{full_log}"
        return f"wazuh-{hashlib.sha256(raw_id_str.encode('utf-8')).hexdigest()[:20]}"

    @classmethod
    def validate_and_normalize_payload(cls, raw_event: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validates event structure and extracts normalized fields.
        Returns (is_valid, error_message, normalized_dict).
        """
        if not isinstance(raw_event, dict):
            return False, "Payload must be a valid JSON object.", {}

        rule = raw_event.get("rule")
        if not rule or not isinstance(rule, dict):
            return False, "Malformed Wazuh event: missing 'rule' object.", {}

        agent = raw_event.get("agent", {})
        if not isinstance(agent, dict):
            agent = {}

        level = rule.get("level", 5)
        try:
            level_num = int(level)
        except (ValueError, TypeError):
            level_num = 5

        # Normalize severity
        if level_num >= 12:
            severity = AlertSeverity.CRITICAL.value
        elif level_num >= 8:
            severity = AlertSeverity.HIGH.value
        elif level_num >= 4:
            severity = AlertSeverity.MEDIUM.value
        else:
            severity = AlertSeverity.LOW.value

        agent_name = agent.get("name") or agent.get("id") or "unknown-endpoint"
        rule_desc = rule.get("description") or raw_event.get("full_log") or "Wazuh Security Event"
        title = f"Wazuh [{agent_name}]: {rule_desc}"

        # Extract MITRE technique IDs if present
        mitre_data = rule.get("mitre", {})
        mitre_ids = []
        if isinstance(mitre_data, dict):
            mitre_ids = mitre_data.get("id", [])
            if isinstance(mitre_ids, str):
                mitre_ids = [mitre_ids]
        elif isinstance(mitre_data, list):
            mitre_ids = mitre_data

        source_event_id = cls.calculate_source_event_id(raw_event)

        normalized = {
            "title": title,
            "source": "Wazuh SIEM Listener",
            "severity": severity,
            "description": rule_desc,
            "source_event_id": source_event_id,
            "agent_id": agent.get("id"),
            "agent_name": agent_name,
            "rule_id": str(rule.get("id", "")),
            "mitre_ids": mitre_ids,
            "raw_payload": raw_event,
        }

        return True, None, normalized

    @classmethod
    async def ingest_wazuh_event(
        cls,
        raw_event: Dict[str, Any],
        tenant_id: str,
        db: AsyncSession,
    ) -> Tuple[bool, Optional[str], Optional[Alert], bool]:
        """
        Ingests a Wazuh event idempotently.
        Returns (success, error_detail, alert_instance, is_duplicate).
        """
        is_valid, err, normalized = cls.validate_and_normalize_payload(raw_event)
        if not is_valid:
            logger.warning("Wazuh event rejected: %s", err)
            return False, err, None, False

        source_event_id = normalized["source_event_id"]

        # Check for existing alert with same source_event_id in this tenant (Idempotency)
        stmt = select(Alert).where(
            Alert.tenant_id == tenant_id,
            Alert.description.contains(f"SourceEventID: {source_event_id}") if False else None
        )
        # Check raw payload or description for idempotent deduplication
        existing_stmt = select(Alert).where(
            Alert.tenant_id == tenant_id,
            Alert.title == normalized["title"],
        ).order_by(Alert.created_at.desc())
        result = await db.execute(existing_stmt)
        existing_alerts = result.scalars().all()

        for alert in existing_alerts:
            payload = alert.raw_payload or {}
            if cls.calculate_source_event_id(payload) == source_event_id:
                logger.info("Idempotent skip: Wazuh alert %s already ingested for tenant %s", alert.alert_id, tenant_id)
                return True, None, alert, True

        # Create new durable alert
        new_alert = Alert(
            tenant_id=tenant_id,
            title=normalized["title"],
            source=normalized["source"],
            severity=normalized["severity"],
            status=AlertStatus.NEW.value,
            description=f"{normalized['description']} | SourceEventID: {source_event_id}",
            raw_payload=normalized["raw_payload"],
        )
        db.add(new_alert)
        await db.commit()
        await db.refresh(new_alert)

        # Publish to real-time SSE stream
        alert_dict = {
            "alert_id": new_alert.alert_id,
            "tenant_id": new_alert.tenant_id,
            "title": new_alert.title,
            "source": new_alert.source,
            "severity": new_alert.severity,
            "status": new_alert.status,
            "description": new_alert.description,
            "source_event_id": source_event_id,
            "created_at": new_alert.created_at.isoformat() if new_alert.created_at else datetime.now(timezone.utc).isoformat(),
        }
        await AlertStreamBroker.publish_alert(tenant_id, alert_dict)

        logger.info("Successfully ingested Wazuh alert %s for tenant %s", new_alert.alert_id, tenant_id)
        return True, None, new_alert, False
