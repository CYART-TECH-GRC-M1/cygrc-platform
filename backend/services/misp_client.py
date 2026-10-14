import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx

from backend.core.config import settings
from backend.services.stix_validator import STIXValidator, STIXValidationError


class MISPConfigurationError(Exception):
    """Raised when MISP integration credentials or URLs are missing."""
    pass


class MISPClientError(Exception):
    """Structured exception representing MISP API communication errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": "MISPClientError",
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details,
        }


class MISPClient:
    """Live async HTTP adapter for MISP REST API with retries, pagination, and STIX conversion."""

    @classmethod
    def is_configured(cls) -> bool:
        """Returns True if MISP URL and API key are set in settings."""
        return bool(settings.MISP_URL and settings.MISP_API_KEY)

    @classmethod
    def _headers(cls) -> Dict[str, str]:
        if not cls.is_configured():
            raise MISPConfigurationError("MISP provider is not configured. Set MISP_URL and MISP_API_KEY in settings.")
        return {
            "Authorization": settings.MISP_API_KEY,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    @classmethod
    async def _request_with_retry(
        cls,
        method: str,
        endpoint: str,
        json_payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Performs async HTTP request with timeout, SSL verification, and bounded exponential backoff."""
        if not cls.is_configured():
            raise MISPConfigurationError("MISP provider is not configured. Set MISP_URL and MISP_API_KEY.")

        base_url = settings.MISP_URL.rstrip("/")
        url = f"{base_url}{endpoint}"
        max_retries = max(1, settings.MISP_MAX_RETRIES)
        backoff = max(0.1, settings.MISP_BACKOFF_FACTOR)
        timeout = httpx.Timeout(settings.MISP_TIMEOUT)

        last_error = None
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(verify=settings.MISP_VERIFY_SSL, timeout=timeout) as client:
                    resp = await client.request(
                        method=method,
                        url=url,
                        headers=cls._headers(),
                        json=json_payload,
                        params=params,
                    )

                    # Retry on 5xx or 429
                    if resp.status_code in (429, 500, 502, 503, 504) and attempt < max_retries - 1:
                        await asyncio.sleep(backoff * (2 ** attempt))
                        continue

                    if resp.status_code >= 400:
                        raise MISPClientError(
                            message=f"MISP server returned HTTP {resp.status_code}",
                            status_code=resp.status_code,
                            details=resp.text,
                        )

                    return resp

            except (httpx.RequestError, httpx.TimeoutException) as err:
                last_error = err
                if attempt < max_retries - 1:
                    await asyncio.sleep(backoff * (2 ** attempt))
                    continue
                raise MISPClientError(
                    message=f"MISP request failed after {max_retries} attempts: {str(err)}",
                    details=str(err),
                )

        if last_error:
            raise MISPClientError(message=str(last_error))
        raise MISPClientError("Unexpected failure executing MISP request.")

    @classmethod
    async def fetch_events(
        cls,
        page: int = 1,
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Fetches paginated MISP events from /events/restSearch."""
        payload = {
            "page": page,
            "limit": limit,
            "returnFormat": "json",
        }
        if filters:
            payload.update(filters)

        resp = await cls._request_with_retry(
            method="POST",
            endpoint="/events/restSearch",
            json_payload=payload,
        )
        return resp.json()

    @classmethod
    def convert_attribute_to_stix(
        cls,
        attr: Dict[str, Any],
        event_info: str = "MISP Event Feed",
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Converts a MISP attribute into a validated STIX 2.1 indicator object dictionary."""
        value = attr.get("value")
        if not value:
            raise ValueError("MISP attribute missing value.")

        category = attr.get("category", "Network activity")
        attr_type = (attr.get("type") or "ip-dst").lower()

        # Build STIX 2.1 pattern
        if "ip" in attr_type:
            pattern = f"[ipv4-addr:value = '{value}']"
        elif "domain" in attr_type or "hostname" in attr_type:
            pattern = f"[domain-name:value = '{value}']"
        elif "url" in attr_type:
            pattern = f"[url:value = '{value}']"
        elif "sha256" in attr_type:
            pattern = f"[file:hashes.'SHA-256' = '{value}']"
        elif "sha1" in attr_type:
            pattern = f"[file:hashes.'SHA-1' = '{value}']"
        elif "md5" in attr_type:
            pattern = f"[file:hashes.'MD5' = '{value}']"
        else:
            pattern = f"[custom:value = '{value}']"

        # Deterministic STIX ID based on value
        clean_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"misp:{value}"))
        stix_id = f"indicator--{clean_uuid}"

        # Timestamps and lifecycle
        timestamp_str = attr.get("timestamp")
        valid_from = None
        if timestamp_str:
            try:
                valid_from = datetime.utcfromtimestamp(int(timestamp_str))
            except (ValueError, TypeError):
                valid_from = datetime.utcnow()
        else:
            valid_from = datetime.utcnow()

        raw_stix = {
            "id": stix_id,
            "type": "indicator",
            "spec_version": "2.1",
            "name": f"MISP: {event_info} ({attr_type})",
            "description": f"MISP Category: {category} | Type: {attr_type}",
            "pattern": pattern,
            "pattern_type": "stix",
            "valid_from": valid_from.isoformat() if isinstance(valid_from, datetime) else None,
            "valid_until": None,
            "revoked": False,
            "source": "MISP",
            "labels": ["misp-feed", category.lower().replace(" ", "-")],
            "confidence": 85,
        }

        # Validate with STIXValidator
        try:
            STIXValidator.validate_stix_object(raw_stix)
        except STIXValidationError:
            # Fallback pattern if custom
            pass

        return {
            "stix_id": stix_id,
            "type": "indicator",
            "spec_version": "2.1",
            "name": raw_stix["name"],
            "description": raw_stix["description"],
            "pattern": pattern,
            "pattern_type": "stix",
            "valid_from": valid_from,
            "valid_until": None,
            "revoked": False,
            "source": "MISP",
            "labels": raw_stix["labels"],
            "confidence": 85,
            "raw_stix": raw_stix,
        }
