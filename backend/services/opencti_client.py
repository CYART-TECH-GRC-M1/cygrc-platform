import asyncio
import uuid
from typing import Dict, Any, List, Optional
import httpx

from backend.core.config import settings
from backend.services.stix_validator import STIXValidator


class OpenCTIConfigurationError(Exception):
    """Raised when OpenCTI GraphQL configuration settings are missing."""
    pass


class OpenCTIClientError(Exception):
    """Structured exception representing OpenCTI API or GraphQL communication errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, errors: Optional[List[Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": "OpenCTIClientError",
            "message": self.message,
            "status_code": self.status_code,
            "errors": self.errors,
        }


class OpenCTIClient:
    """Live async GraphQL client adapter for OpenCTI threat intel server."""

    @classmethod
    def is_configured(cls) -> bool:
        """Returns True if OpenCTI URL and API key are configured."""
        return bool(settings.OPENCTI_URL and settings.OPENCTI_API_KEY)

    @classmethod
    def _headers(cls) -> Dict[str, str]:
        if not cls.is_configured():
            raise OpenCTIConfigurationError(
                "OpenCTI provider is not configured. Set OPENCTI_URL and OPENCTI_API_KEY in settings."
            )
        return {
            "Authorization": f"Bearer {settings.OPENCTI_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @classmethod
    async def execute_graphql(
        cls,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Executes a GraphQL query against OpenCTI with retries, timeout, and backoff."""
        if not cls.is_configured():
            raise OpenCTIConfigurationError("OpenCTI provider is not configured. Set OPENCTI_URL and OPENCTI_API_KEY.")

        url = settings.OPENCTI_URL.rstrip("/")
        max_retries = max(1, settings.OPENCTI_MAX_RETRIES)
        backoff = max(0.1, settings.OPENCTI_BACKOFF_FACTOR)
        timeout = httpx.Timeout(settings.OPENCTI_TIMEOUT)

        payload = {"query": query, "variables": variables or {}}
        last_error = None

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(verify=settings.OPENCTI_VERIFY_SSL, timeout=timeout) as client:
                    resp = await client.post(
                        url=url,
                        headers=cls._headers(),
                        json=payload,
                    )

                    if resp.status_code in (429, 500, 502, 503, 504) and attempt < max_retries - 1:
                        await asyncio.sleep(backoff * (2 ** attempt))
                        continue

                    if resp.status_code >= 400:
                        raise OpenCTIClientError(
                            message=f"OpenCTI server returned HTTP {resp.status_code}",
                            status_code=resp.status_code,
                            errors=[resp.text],
                        )

                    data = resp.json()
                    if "errors" in data and data["errors"]:
                        raise OpenCTIClientError(
                            message=f"GraphQL query error: {data['errors'][0].get('message', 'Unknown error')}",
                            status_code=200,
                            errors=data["errors"],
                        )

                    return data

            except (httpx.RequestError, httpx.TimeoutException) as err:
                last_error = err
                if attempt < max_retries - 1:
                    await asyncio.sleep(backoff * (2 ** attempt))
                    continue
                raise OpenCTIClientError(
                    message=f"OpenCTI request failed after {max_retries} attempts: {str(err)}",
                    errors=[str(err)],
                )

        if last_error:
            raise OpenCTIClientError(message=str(last_error))
        raise OpenCTIClientError("Unexpected failure executing OpenCTI GraphQL request.")

    @classmethod
    async def fetch_indicators(
        cls,
        first: int = 50,
        after: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetches paginated STIX indicators from OpenCTI GraphQL API."""
        query = """
        query GetIndicators($first: Int, $after: String) {
          indicators(first: $first, after: $after) {
            pageInfo {
              hasNextPage
              endCursor
            }
            edges {
              node {
                id
                standard_id
                entity_type
                name
                description
                pattern
                pattern_type
                valid_from
                valid_until
                revoked
                confidence
                created
                modified
              }
            }
          }
        }
        """
        variables = {"first": first, "after": after}
        return await cls.execute_graphql(query, variables)

    @classmethod
    def convert_opencti_node_to_stix(
        cls,
        node: Dict[str, Any],
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Converts an OpenCTI GraphQL node into a validated STIX 2.1 indicator object."""
        raw_id = node.get("standard_id") or node.get("id")
        entity_type = (node.get("entity_type") or "indicator").lower()

        # Format STIX ID correctly
        if raw_id and STIXValidator.STIX_ID_REGEX.match(raw_id):
            stix_id = raw_id
        else:
            clean_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"opencti:{raw_id or node.get('name', '')}"))
            stix_id = f"{entity_type}--{clean_uuid}"

        name = node.get("name") or "OpenCTI Indicator"
        pattern = node.get("pattern") or f"[{entity_type}:name = '{name}']"
        pattern_type = (node.get("pattern_type") or "stix").lower()
        confidence = node.get("confidence", 90)
        revoked = bool(node.get("revoked", False))

        timestamps = STIXValidator.validate_timestamps(
            created=node.get("created"),
            modified=node.get("modified"),
            valid_from=node.get("valid_from"),
            valid_until=node.get("valid_until"),
        )

        raw_stix = {
            "id": stix_id,
            "type": entity_type,
            "spec_version": "2.1",
            "name": name,
            "description": node.get("description"),
            "pattern": pattern,
            "pattern_type": pattern_type,
            "valid_from": timestamps["valid_from"].isoformat() if timestamps["valid_from"] else None,
            "valid_until": timestamps["valid_until"].isoformat() if timestamps["valid_until"] else None,
            "revoked": revoked,
            "confidence": confidence if isinstance(confidence, int) else 90,
            "source": "OpenCTI",
            "labels": ["opencti-graphql"],
        }

        return {
            "stix_id": stix_id,
            "type": entity_type,
            "spec_version": "2.1",
            "name": name,
            "description": node.get("description"),
            "pattern": pattern,
            "pattern_type": pattern_type,
            "valid_from": timestamps["valid_from"],
            "valid_until": timestamps["valid_until"],
            "revoked": revoked,
            "source": "OpenCTI",
            "labels": ["opencti-graphql"],
            "confidence": confidence if isinstance(confidence, int) else 90,
            "raw_stix": raw_stix,
        }
