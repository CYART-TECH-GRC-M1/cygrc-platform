import re
from datetime import datetime
from typing import Dict, Any, List, Set, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.alert import Alert
from backend.models.stix_object import StixObject


class AlertEnrichmentService:
    """Enriches incoming SOC alerts against stored STIX 2.1 threat intel indicators."""

    IPV4_REGEX = re.compile(
        r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    )
    DOMAIN_REGEX = re.compile(
        r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b"
    )
    URL_REGEX = re.compile(
        r"https?://[^\s<>\"']+"
    )
    SHA256_REGEX = re.compile(r"\b[a-fA-F0-9]{64}\b")
    SHA1_REGEX = re.compile(r"\b[a-fA-F0-9]{40}\b")
    MD5_REGEX = re.compile(r"\b[a-fA-F0-9]{32}\b")

    @classmethod
    def extract_observables_from_text(cls, text: str) -> Dict[str, Set[str]]:
        """Extracts and normalizes IP addresses, domains, URLs, and file hashes from text."""
        if not text:
            return {
                "ips": set(),
                "domains": set(),
                "urls": set(),
                "hashes": set(),
            }

        ips = set(cls.IPV4_REGEX.findall(text))
        urls = set(cls.URL_REGEX.findall(text))

        # Domains, excluding pure IP occurrences and URL sub-components
        raw_domains = set(cls.DOMAIN_REGEX.findall(text))
        domains = set()
        for d in raw_domains:
            d_norm = d.strip().lower().rstrip(".")
            # Filter common false positives like file extensions
            if not d_norm.endswith((".py", ".exe", ".log", ".json", ".txt", ".js")):
                domains.add(d_norm)

        # Hashes normalized to lowercase
        sha256 = {h.lower() for h in cls.SHA256_REGEX.findall(text)}
        sha1 = {h.lower() for h in cls.SHA1_REGEX.findall(text)}
        md5 = {h.lower() for h in cls.MD5_REGEX.findall(text)}
        hashes = sha256 | sha1 | md5

        return {
            "ips": ips,
            "domains": domains,
            "urls": urls,
            "hashes": hashes,
        }

    @classmethod
    def extract_all_observables(cls, alert: Alert) -> Dict[str, Set[str]]:
        """Recursively traverses alert fields and payload to extract all candidate IOC observables."""
        texts: List[str] = [alert.title or "", alert.description or ""]

        def recurse_payload(data: Any):
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, (dict, list)):
                        recurse_payload(v)
                    elif v is not None:
                        texts.append(str(v))
            elif isinstance(data, list):
                for item in data:
                    recurse_payload(item)
            elif data is not None:
                texts.append(str(data))

        if alert.raw_payload:
            recurse_payload(alert.raw_payload)

        combined_text = " ".join(texts)
        return cls.extract_observables_from_text(combined_text)

    @staticmethod
    def is_indicator_active(indicator: StixObject, now: Optional[datetime] = None) -> bool:
        """Determines if a STIX indicator is currently active (not revoked and within validity bounds)."""
        current_time = now or datetime.utcnow()

        # 1. Exclude revoked indicators
        if indicator.revoked:
            return False

        # 2. Exclude expired indicators
        if indicator.valid_until and indicator.valid_until < current_time:
            return False

        # 3. Exclude not-yet-valid indicators
        if indicator.valid_from and indicator.valid_from > current_time:
            return False

        return True

    @classmethod
    async def enrich_alert_with_stix(
        cls,
        alert_id: str,
        tenant_id: str,
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """Enriches an alert by matching active IOCs against tenant STIX indicators."""
        stmt = select(Alert).where(Alert.alert_id == alert_id, Alert.tenant_id == tenant_id)
        result = await db.execute(stmt)
        alert = result.scalar_one_or_none()

        if not alert:
            return {"success": False, "error": "Alert not found"}

        # Extract normalized observables from alert
        observables = cls.extract_all_observables(alert)
        all_observables = (
            observables["ips"] | observables["domains"] | observables["urls"] | observables["hashes"]
        )

        full_alert_text = f"{alert.title} {alert.description or ''} {str(alert.raw_payload or {})}"

        # Query STIX objects for THIS tenant only (tenant isolation)
        stix_stmt = select(StixObject).where(StixObject.tenant_id == tenant_id)
        stix_result = await db.execute(stix_stmt)
        stix_items = stix_result.scalars().all()

        now = datetime.utcnow()
        matched_stix = []

        for item in stix_items:
            # Lifecycle filter: exclude revoked and expired indicators
            if not cls.is_indicator_active(item, now=now):
                continue

            pattern = item.pattern or ""
            # Extract raw indicator value inside quotes e.g. [ipv4-addr:value = '198.51.100.42'] -> 198.51.100.42
            matches = re.findall(r"'(.*?)'", pattern)
            target_val = matches[0] if matches else item.name

            if not target_val:
                continue

            target_val_clean = target_val.strip()
            target_val_lower = target_val_clean.lower()

            # Match against extracted observables or full alert text
            is_matched = (
                target_val_clean in all_observables
                or target_val_lower in {o.lower() for o in all_observables}
                or target_val_clean in full_alert_text
            )

            if is_matched:
                matched_stix.append({
                    "stix_id": item.stix_id,
                    "type": item.type,
                    "name": item.name,
                    "pattern": item.pattern,
                    "pattern_type": item.pattern_type,
                    "confidence": item.confidence or 50,
                    "source": item.source,
                    "valid_from": item.valid_from.isoformat() if item.valid_from else None,
                    "valid_until": item.valid_until.isoformat() if item.valid_until else None,
                    "revoked": item.revoked,
                    "labels": item.labels,
                    "matched_observable": target_val_clean,
                })

        enrichment_data = {
            "enriched": True,
            "matched_indicators_count": len(matched_stix),
            "indicators": matched_stix,
            "extracted_observables": {
                "ips": list(observables["ips"]),
                "domains": list(observables["domains"]),
                "urls": list(observables["urls"]),
                "hashes": list(observables["hashes"]),
            },
            "threat_confidence": max([m["confidence"] for m in matched_stix], default=0),
        }

        current_payload = dict(alert.raw_payload or {})
        current_payload["threat_intel_enrichment"] = enrichment_data
        alert.raw_payload = current_payload

        # Auto-escalate alert severity if matched with high-confidence active threat indicator (>= 80)
        if len(matched_stix) > 0 and enrichment_data["threat_confidence"] >= 80:
            alert.severity = "CRITICAL"

        await db.commit()
        await db.refresh(alert)

        return {
            "success": True,
            "alert_id": alert_id,
            "enrichment": enrichment_data,
        }

    @classmethod
    async def enrich_alerts_batch(
        cls,
        alert_ids: List[str],
        tenant_id: str,
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """Batch enrichment of multiple SOC alerts with tenant isolation."""
        results = []
        for aid in alert_ids:
            res = await cls.enrich_alert_with_stix(alert_id=aid, tenant_id=tenant_id, db=db)
            results.append(res)

        return {
            "total_requested": len(alert_ids),
            "successful_count": sum(1 for r in results if r.get("success")),
            "failed_count": sum(1 for r in results if not r.get("success")),
            "results": results,
        }
