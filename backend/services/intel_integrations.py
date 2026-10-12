import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.stix_object import StixObject
from backend.services.misp_client import MISPClient, MISPConfigurationError, MISPClientError
from backend.services.opencti_client import OpenCTIClient, OpenCTIConfigurationError, OpenCTIClientError
from backend.services.stix_validator import STIXValidator, STIXValidationError


class IntelIntegrationService:
    """MISP and OpenCTI threat intelligence client integration and ingestion service."""

    @staticmethod
    def _resolve_tenant_stix_id(stix_id: str, tenant_id: str) -> str:
        """Deterministic tenant-scoped STIX ID collision resolution."""
        tenant_prefix = tenant_id[:8]
        if f"-{tenant_prefix}" not in stix_id:
            return f"{stix_id}-{tenant_prefix}"
        return stix_id

    @classmethod
    async def sync_misp_events(
        cls,
        misp_payload: Dict[str, Any],
        tenant_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Parses MISP Event attributes and converts into STIX 2.1 Indicators with tenant isolation."""
        event = misp_payload.get("Event", {})
        info = event.get("info", "MISP Event Feed")
        attributes = event.get("Attribute", [])

        stix_objects_created = 0

        for attr in attributes:
            value = attr.get("value")
            category = attr.get("category", "Network activity")
            attr_type = attr.get("type", "ip-dst")

            if not value:
                continue

            # Determine STIX pattern
            if "ip" in attr_type:
                pattern = f"[ipv4-addr:value = '{value}']"
            elif "domain" in attr_type:
                pattern = f"[domain-name:value = '{value}']"
            elif "url" in attr_type:
                pattern = f"[url:value = '{value}']"
            elif "hash" in attr_type or "md5" in attr_type or "sha256" in attr_type:
                pattern = f"[file:hashes.'SHA-256' = '{value}']"
            else:
                pattern = f"[custom:value = '{value}']"

            clean_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(value)))
            stix_id = f"indicator--{clean_uuid}"

            # Check existing for THIS tenant specifically (tenant isolation)
            stmt = select(StixObject).where(
                StixObject.stix_id == stix_id,
                StixObject.tenant_id == tenant_id,
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            # Prevent cross-tenant ID collisions: never overwrite another tenant's record
            if not existing:
                collision_stmt = select(StixObject).where(
                    StixObject.stix_id == stix_id,
                    StixObject.tenant_id != tenant_id,
                )
                if (await db.execute(collision_stmt)).scalar_one_or_none():
                    stix_id = cls._resolve_tenant_stix_id(stix_id, tenant_id)

            raw_stix = {
                "id": stix_id,
                "type": "indicator",
                "spec_version": "2.1",
                "name": f"MISP: {info} ({attr_type})",
                "description": f"MISP Category: {category} | Type: {attr_type}",
                "pattern": pattern,
                "pattern_type": "stix",
                "valid_from": datetime.utcnow().isoformat(),
                "valid_until": None,
                "revoked": False,
                "source": "MISP",
                "labels": ["misp-feed", category.lower().replace(" ", "-")],
                "confidence": 85,
            }

            if existing:
                existing.name = raw_stix["name"]
                existing.description = raw_stix["description"]
                existing.pattern = pattern
                existing.pattern_type = "stix"
                existing.revoked = False
                existing.source = "MISP"
                existing.raw_stix = raw_stix
                existing.modified_at = datetime.utcnow()
            else:
                stix_obj = StixObject(
                    stix_id=stix_id,
                    tenant_id=tenant_id,
                    type="indicator",
                    spec_version="2.1",
                    name=raw_stix["name"],
                    description=raw_stix["description"],
                    pattern=pattern,
                    pattern_type="stix",
                    valid_from=datetime.utcnow(),
                    valid_until=None,
                    revoked=False,
                    source="MISP",
                    labels=raw_stix["labels"],
                    confidence=85,
                    raw_stix=raw_stix,
                )
                db.add(stix_obj)

            stix_objects_created += 1

        await db.commit()
        return {
            "status": "SUCCESS",
            "misp_info": info,
            "stix_objects_ingested": stix_objects_created,
            "timestamp": datetime.utcnow()
        }

    @classmethod
    async def sync_misp_live(
        cls,
        tenant_id: str,
        db: AsyncSession,
        page: int = 1,
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Live HTTP client sync from configured MISP instance with bounded retries."""
        if not MISPClient.is_configured():
            return {
                "status": "UNCONFIGURED",
                "provider": "MISP",
                "message": "MISP provider is not configured. Set MISP_URL and MISP_API_KEY in settings.",
                "stix_objects_ingested": 0,
            }

        try:
            data = await MISPClient.fetch_events(page=page, limit=limit, filters=filters)
        except (MISPConfigurationError, MISPClientError) as err:
            return {
                "status": "ERROR",
                "provider": "MISP",
                "error": str(err),
                "stix_objects_ingested": 0,
            }

        response_list = data.get("response", [])
        total_ingested = 0
        events_processed = 0

        for item in response_list:
            event_payload = item if "Event" in item else {"Event": item}
            sync_res = await cls.sync_misp_events(event_payload, tenant_id=tenant_id, db=db)
            total_ingested += sync_res.get("stix_objects_ingested", 0)
            events_processed += 1

        return {
            "status": "SUCCESS",
            "provider": "MISP",
            "events_processed": events_processed,
            "stix_objects_ingested": total_ingested,
            "page": page,
            "limit": limit,
            "timestamp": datetime.utcnow(),
        }

    @classmethod
    async def sync_opencti_graphql(
        cls,
        graphql_data: Dict[str, Any],
        tenant_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Parses OpenCTI GraphQL STIX entity payloads and stores in stix_objects with tenant isolation."""
        entities = graphql_data.get("data", {}).get("stixDomainObjects", [])
        ingested = 0

        for entity in entities:
            stix_id = entity.get("id") or f"opencti--{uuid.uuid4()}"
            stix_type = entity.get("entity_type", "indicator").lower()
            name = entity.get("name") or entity.get("observable_value") or "OpenCTI Entity"
            pattern = entity.get("pattern") or f"[{stix_type}:name = '{name}']"
            confidence = entity.get("confidence", 90)
            pattern_type = (entity.get("pattern_type") or "stix").lower()
            revoked = bool(entity.get("revoked", False))

            raw_stix = {
                "id": stix_id,
                "type": stix_type,
                "spec_version": "2.1",
                "name": name,
                "description": entity.get("description"),
                "pattern": pattern,
                "pattern_type": pattern_type,
                "valid_from": entity.get("valid_from"),
                "valid_until": entity.get("valid_until"),
                "revoked": revoked,
                "source": "OpenCTI",
                "labels": ["opencti-graphql"],
                "confidence": confidence if isinstance(confidence, int) else 90,
            }

            stmt = select(StixObject).where(
                StixObject.stix_id == stix_id,
                StixObject.tenant_id == tenant_id,
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            # Prevent cross-tenant collisions
            if not existing:
                collision_stmt = select(StixObject).where(
                    StixObject.stix_id == stix_id,
                    StixObject.tenant_id != tenant_id,
                )
                if (await db.execute(collision_stmt)).scalar_one_or_none():
                    stix_id = cls._resolve_tenant_stix_id(stix_id, tenant_id)
                    raw_stix["id"] = stix_id

            if existing:
                existing.name = name
                existing.description = entity.get("description")
                existing.pattern = pattern
                existing.pattern_type = pattern_type
                existing.revoked = revoked
                existing.source = "OpenCTI"
                existing.raw_stix = raw_stix
                existing.modified_at = datetime.utcnow()
            else:
                stix_obj = StixObject(
                    stix_id=stix_id,
                    tenant_id=tenant_id,
                    type=stix_type,
                    spec_version="2.1",
                    name=name,
                    description=entity.get("description"),
                    pattern=pattern,
                    pattern_type=pattern_type,
                    valid_from=None,
                    valid_until=None,
                    revoked=revoked,
                    source="OpenCTI",
                    labels=["opencti-graphql"],
                    confidence=confidence if isinstance(confidence, int) else 90,
                    raw_stix=raw_stix,
                )
                db.add(stix_obj)
            ingested += 1

        await db.commit()
        return {
            "status": "SUCCESS",
            "opencti_entities_ingested": ingested,
            "timestamp": datetime.utcnow()
        }

    @classmethod
    async def sync_opencti_live(
        cls,
        tenant_id: str,
        db: AsyncSession,
        first: int = 50,
        after: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Live GraphQL sync from configured OpenCTI instance with bounded retries."""
        if not OpenCTIClient.is_configured():
            return {
                "status": "UNCONFIGURED",
                "provider": "OpenCTI",
                "message": "OpenCTI provider is not configured. Set OPENCTI_URL and OPENCTI_API_KEY in settings.",
                "indicators_ingested": 0,
            }

        try:
            data = await OpenCTIClient.fetch_indicators(first=first, after=after)
        except (OpenCTIConfigurationError, OpenCTIClientError) as err:
            return {
                "status": "ERROR",
                "provider": "OpenCTI",
                "error": str(err),
                "indicators_ingested": 0,
            }

        indicators_data = data.get("data", {}).get("indicators", {})
        edges = indicators_data.get("edges", [])
        page_info = indicators_data.get("pageInfo", {})

        ingested_count = 0
        for edge in edges:
            node = edge.get("node", {})
            stix_dict = OpenCTIClient.convert_opencti_node_to_stix(node, tenant_id=tenant_id)
            stix_id = stix_dict["stix_id"]

            stmt = select(StixObject).where(
                StixObject.stix_id == stix_id,
                StixObject.tenant_id == tenant_id,
            )
            existing = (await db.execute(stmt)).scalar_one_or_none()

            if not existing:
                collision_stmt = select(StixObject).where(
                    StixObject.stix_id == stix_id,
                    StixObject.tenant_id != tenant_id,
                )
                if (await db.execute(collision_stmt)).scalar_one_or_none():
                    stix_id = cls._resolve_tenant_stix_id(stix_id, tenant_id)
                    stix_dict["stix_id"] = stix_id
                    stix_dict["raw_stix"]["id"] = stix_id

            if existing:
                existing.name = stix_dict["name"]
                existing.description = stix_dict["description"]
                existing.pattern = stix_dict["pattern"]
                existing.pattern_type = stix_dict["pattern_type"]
                existing.valid_from = stix_dict["valid_from"]
                existing.valid_until = stix_dict["valid_until"]
                existing.revoked = stix_dict["revoked"]
                existing.source = stix_dict["source"]
                existing.raw_stix = stix_dict["raw_stix"]
                existing.modified_at = datetime.utcnow()
            else:
                new_obj = StixObject(
                    stix_id=stix_id,
                    tenant_id=tenant_id,
                    type=stix_dict["type"],
                    spec_version=stix_dict["spec_version"],
                    name=stix_dict["name"],
                    description=stix_dict["description"],
                    pattern=stix_dict["pattern"],
                    pattern_type=stix_dict["pattern_type"],
                    valid_from=stix_dict["valid_from"],
                    valid_until=stix_dict["valid_until"],
                    revoked=stix_dict["revoked"],
                    source=stix_dict["source"],
                    labels=stix_dict["labels"],
                    confidence=stix_dict["confidence"],
                    raw_stix=stix_dict["raw_stix"],
                )
                db.add(new_obj)
            ingested_count += 1

        await db.commit()
        return {
            "status": "SUCCESS",
            "provider": "OpenCTI",
            "indicators_ingested": ingested_count,
            "page_info": page_info,
            "timestamp": datetime.utcnow(),
        }
