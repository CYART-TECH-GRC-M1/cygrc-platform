from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.models.stix_object import StixObject

router = APIRouter()

TAXII_MEDIA_TYPE = "application/taxii+json;version=2.1"


class TaxiiDiscoveryResponse(BaseModel):
    title: str = "CyGRC TAXII 2.1 Threat Intel Server"
    description: str = "Ingestion and distribution point for STIX 2.1 threat intelligence feeds"
    default: str = "/api/v1/taxii2/"
    api_roots: List[str] = ["/api/v1/taxii2/"]


class TaxiiCollection(BaseModel):
    id: str
    title: str
    description: str
    can_read: bool = True
    can_write: bool = True
    media_types: List[str] = ["application/stix+json;version=2.1"]


class TaxiiCollectionsResponse(BaseModel):
    collections: List[TaxiiCollection]


class StixBundleIngestRequest(BaseModel):
    type: str = "bundle"
    id: str
    objects: List[Dict[str, Any]]


@router.get("", response_model=TaxiiDiscoveryResponse)
@router.get("/", response_model=TaxiiDiscoveryResponse)
async def taxii_discovery():
    """TAXII 2.1 Discovery Endpoint."""
    return TaxiiDiscoveryResponse()


@router.get("/collections/", response_model=TaxiiCollectionsResponse)
async def list_taxii_collections():
    """List available TAXII 2.1 Threat Intel Collections."""
    return TaxiiCollectionsResponse(
        collections=[
            TaxiiCollection(
                id="default-threat-intel",
                title="Default CyGRC Threat Feed",
                description="Aggregated STIX 2.1 Indicators, Malware, and Threat Actor objects"
            ),
            TaxiiCollection(
                id="misp-opencti-feed",
                title="MISP & OpenCTI Live Feeds",
                description="High-confidence external threat intelligence feeds"
            )
        ]
    )


@router.post("/collections/{collection_id}/objects/", status_code=status.HTTP_202_ACCEPTED)
async def ingest_stix_bundle(
    collection_id: str,
    payload: StixBundleIngestRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Ingest STIX 2.1 Bundle of threat intel objects via TAXII 2.1 Server."""
    ingested_count = 0
    objects = payload.objects or []

    for obj in objects:
        stix_id = obj.get("id") or f"{obj.get('type', 'indicator')}--{uuid.uuid4()}"
        stix_type = obj.get("type", "indicator").lower()

        # Extract standard fields
        name = obj.get("name")
        description = obj.get("description")
        pattern = obj.get("pattern")
        labels = obj.get("labels", [])
        confidence = obj.get("confidence", 75)

        # Check existing for THIS tenant specifically (tenant isolation)
        stmt = select(StixObject).where(
            StixObject.stix_id == stix_id,
            StixObject.tenant_id == tenant_id,
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if not existing:
            collision_stmt = select(StixObject).where(
                StixObject.stix_id == stix_id,
                StixObject.tenant_id != tenant_id,
            )
            if (await db.execute(collision_stmt)).scalar_one_or_none():
                stix_id = f"{stix_id}-{tenant_id[:8]}"

        if existing:
            existing.name = name
            existing.description = description
            existing.pattern = pattern
            existing.labels = labels
            existing.confidence = confidence
            existing.raw_stix = obj
            existing.modified_at = datetime.utcnow()
        else:
            new_stix = StixObject(
                stix_id=stix_id,
                tenant_id=tenant_id,
                type=stix_type,
                spec_version="2.1",
                name=name,
                description=description,
                pattern=pattern,
                labels=labels,
                confidence=confidence,
                raw_stix=obj,
            )
            db.add(new_stix)
        ingested_count += 1

    await db.commit()

    return {
        "status": "SUCCESS",
        "collection_id": collection_id,
        "bundle_id": payload.id,
        "objects_ingested": ingested_count,
        "timestamp": datetime.utcnow()
    }


@router.get("/collections/{collection_id}/objects/")
async def get_taxii_objects(
    collection_id: str,
    type_filter: Optional[str] = Query(None, alias="type"),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve STIX 2.1 objects from TAXII 2.1 collection."""
    stmt = select(StixObject).where(StixObject.tenant_id == tenant_id)
    if type_filter:
        stmt = stmt.where(StixObject.type == type_filter.lower())
    result = await db.execute(stmt)
    stix_items = result.scalars().all()

    stix_objects = [item.raw_stix or {
        "id": item.stix_id,
        "type": item.type,
        "spec_version": item.spec_version,
        "name": item.name,
        "description": item.description,
        "pattern": item.pattern,
        "labels": item.labels,
        "confidence": item.confidence
    } for item in stix_items]

    return {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "objects": stix_objects
    }
