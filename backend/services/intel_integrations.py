import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.stix_object import StixObject


class IntelIntegrationService:
    """MISP and OpenCTI threat intelligence client integration service."""

    @staticmethod
    async def sync_misp_events(
        misp_payload: Dict[str, Any],
        tenant_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Parses MISP Event attributes and converts into STIX 2.1 Indicators."""
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
                stix_type = "indicator"
            elif "domain" in attr_type:
                pattern = f"[domain-name:value = '{value}']"
                stix_type = "indicator"
            elif "hash" in attr_type or "md5" in attr_type or "sha256" in attr_type:
                pattern = f"[file:hashes.'SHA-256' = '{value}']"
                stix_type = "indicator"
            else:
                pattern = f"[custom:value = '{value}']"
                stix_type = "indicator"

            stix_id = f"indicator--misp-{uuid.uuid5(uuid.NAMESPACE_DNS, str(value))}"

            # Check existing for THIS tenant specifically (tenant isolation)
            stmt = select(StixObject).where(
                StixObject.stix_id == stix_id,
                StixObject.tenant_id == tenant_id,
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            # If the stix_id exists for another tenant, scope the id with tenant prefix to avoid collision
            if not existing:
                collision_stmt = select(StixObject).where(
                    StixObject.stix_id == stix_id,
                    StixObject.tenant_id != tenant_id,
                )
                if (await db.execute(collision_stmt)).scalar_one_or_none():
                    stix_id = f"indicator--misp-{tenant_id[:8]}-{uuid.uuid5(uuid.NAMESPACE_DNS, str(value))}"

            raw_stix = {
                "id": stix_id,
                "type": stix_type,
                "spec_version": "2.1",
                "name": f"MISP: {info} ({attr_type})",
                "pattern": pattern,
                "labels": ["misp-feed", category.lower().replace(" ", "-")],
                "confidence": 85
            }

            if existing:
                existing.name = raw_stix["name"]
                existing.pattern = pattern
                existing.modified_at = datetime.utcnow()
            else:
                stix_obj = StixObject(
                    stix_id=stix_id,
                    tenant_id=tenant_id,
                    type=stix_type,
                    spec_version="2.1",
                    name=raw_stix["name"],
                    description=f"MISP Category: {category} | Type: {attr_type}",
                    pattern=pattern,
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

    @staticmethod
    async def sync_opencti_graphql(
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

            raw_stix = {
                "id": stix_id,
                "type": stix_type,
                "spec_version": "2.1",
                "name": name,
                "description": entity.get("description"),
                "pattern": pattern,
                "labels": ["opencti-graphql"],
                "confidence": entity.get("confidence", 90)
            }

            stmt = select(StixObject).where(
                StixObject.stix_id == stix_id,
                StixObject.tenant_id == tenant_id,
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            # If the stix_id exists for another tenant, scope the id to prevent collision/tampering
            if not existing:
                collision_stmt = select(StixObject).where(
                    StixObject.stix_id == stix_id,
                    StixObject.tenant_id != tenant_id,
                )
                if (await db.execute(collision_stmt)).scalar_one_or_none():
                    stix_id = f"{stix_id}-{tenant_id[:8]}"
                    raw_stix["id"] = stix_id

            if existing:
                existing.name = name
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
                    labels=["opencti-graphql"],
                    confidence=90,
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
