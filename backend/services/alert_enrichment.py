import re
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.alert import Alert
from backend.models.stix_object import StixObject


class AlertEnrichmentService:
    """Enriches incoming SOC alerts against stored STIX 2.1 threat intel indicators."""

    @staticmethod
    async def enrich_alert_with_stix(
        alert_id: str,
        tenant_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        stmt = select(Alert).where(Alert.alert_id == alert_id, Alert.tenant_id == tenant_id)
        result = await db.execute(stmt)
        alert = result.scalar_one_or_none()

        if not alert:
            return {"success": False, "error": "Alert not found"}

        payload = alert.raw_payload or {}
        description = f"{alert.title} {alert.description or ''} {str(payload)}"

        # Query all STIX objects for tenant
        stix_stmt = select(StixObject).where(StixObject.tenant_id == tenant_id)
        stix_result = await db.execute(stix_stmt)
        stix_items = stix_result.scalars().all()

        matched_stix = []

        for item in stix_items:
            # Match pattern value inside alert description/payload
            pattern = item.pattern or ""
            # Extract raw indicator value inside quotes e.g. [ipv4-addr:value = '198.51.100.42'] -> 198.51.100.42
            matches = re.findall(r"'(.*?)'", pattern)
            target_val = matches[0] if matches else item.name

            if target_val and target_val in description:
                matched_stix.append({
                    "stix_id": item.stix_id,
                    "type": item.type,
                    "name": item.name,
                    "pattern": item.pattern,
                    "confidence": item.confidence,
                    "labels": item.labels,
                })

        # Decorate alert raw payload with threat intel enrichment
        enrichment_data = {
            "enriched": True,
            "matched_indicators_count": len(matched_stix),
            "indicators": matched_stix,
            "threat_confidence": max([m["confidence"] for m in matched_stix], default=0)
        }

        current_payload = dict(alert.raw_payload or {})
        current_payload["threat_intel_enrichment"] = enrichment_data
        alert.raw_payload = current_payload

        # Auto-escalate alert severity if matched with high-confidence threat indicator
        if len(matched_stix) > 0 and enrichment_data["threat_confidence"] >= 80:
            alert.severity = "CRITICAL"

        await db.commit()
        await db.refresh(alert)

        return {
            "success": True,
            "alert_id": alert_id,
            "enrichment": enrichment_data
        }
