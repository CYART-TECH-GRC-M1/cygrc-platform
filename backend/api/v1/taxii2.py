from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header, Query, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.models.stix_object import StixObject
from backend.services.stix_validator import STIXValidator, STIXValidationError

router = APIRouter()

TAXII_MEDIA_TYPE = "application/taxii+json;version=2.1"
STIX_MEDIA_TYPE = "application/stix+json;version=2.1"

# In-memory TAXII Status tracker
_taxii_status_store: Dict[str, Dict[str, Any]] = {}


def taxii_json_response(content: Any, status_code: int = 200, media_type: str = TAXII_MEDIA_TYPE) -> JSONResponse:
    """Helper ensuring correct TAXII/STIX 2.1 media type headers."""
    return JSONResponse(
        content=content,
        status_code=status_code,
        headers={"Content-Type": media_type},
    )


def taxii_error(title: str, description: str, http_status: int = 404) -> JSONResponse:
    """Standard TAXII 2.1 error response."""
    return taxii_json_response(
        content={
            "title": title,
            "description": description,
            "error_id": str(uuid.uuid4()),
            "http_status": str(http_status),
        },
        status_code=http_status,
        media_type=TAXII_MEDIA_TYPE,
    )


class TaxiiDiscoveryResponse(BaseModel):
    title: str = "CyGRC TAXII 2.1 Threat Intel Server"
    description: str = "Ingestion and distribution point for STIX 2.1 threat intelligence feeds"
    contact: str = "secops@cygrc.local"
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


AVAILABLE_COLLECTIONS = {
    "default-threat-intel": TaxiiCollection(
        id="default-threat-intel",
        title="Default CyGRC Threat Feed",
        description="Aggregated STIX 2.1 Indicators, Malware, and Threat Actor objects",
    ),
    "misp-opencti-feed": TaxiiCollection(
        id="misp-opencti-feed",
        title="MISP & OpenCTI Live Feeds",
        description="High-confidence external threat intelligence feeds",
    ),
    "soc-indicators": TaxiiCollection(
        id="soc-indicators",
        title="SOC Detected Indicators",
        description="Tenant-specific verified IOCs and detection indicators",
    ),
}


@router.get("", response_model=TaxiiDiscoveryResponse)
@router.get("/", response_model=TaxiiDiscoveryResponse)
async def taxii_discovery(response: Response):
    """TAXII 2.1 Server Discovery Endpoint."""
    response.headers["Content-Type"] = TAXII_MEDIA_TYPE
    return TaxiiDiscoveryResponse()


@router.get("/collections/", response_model=TaxiiCollectionsResponse)
async def list_taxii_collections(response: Response):
    """List available TAXII 2.1 Threat Intel Collections."""
    response.headers["Content-Type"] = TAXII_MEDIA_TYPE
    return TaxiiCollectionsResponse(collections=list(AVAILABLE_COLLECTIONS.values()))


@router.get("/collections/{collection_id}/")
async def get_taxii_collection(collection_id: str, response: Response):
    """Retrieve detailed metadata for a specific TAXII 2.1 Collection."""
    coll = AVAILABLE_COLLECTIONS.get(collection_id)
    if not coll:
        return taxii_error(
            title="Collection Not Found",
            description=f"Collection '{collection_id}' does not exist on this TAXII server.",
            http_status=404,
        )
    response.headers["Content-Type"] = TAXII_MEDIA_TYPE
    return coll.dict()


@router.get("/status/{status_id}/")
async def get_taxii_status(status_id: str, response: Response):
    """Retrieve tracking status for an asynchronous or batched TAXII ingest job."""
    record = _taxii_status_store.get(status_id)
    if not record:
        return taxii_error(
            title="Status Not Found",
            description=f"Status record '{status_id}' not found.",
            http_status=404,
        )
    response.headers["Content-Type"] = TAXII_MEDIA_TYPE
    return record


@router.post("/collections/{collection_id}/objects/", status_code=status.HTTP_202_ACCEPTED)
async def ingest_stix_bundle(
    collection_id: str,
    payload: StixBundleIngestRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Ingest STIX 2.1 Bundle of threat intel objects with status tracking and tenant isolation."""
    coll = AVAILABLE_COLLECTIONS.get(collection_id)
    if not coll:
        return taxii_error(
            title="Collection Not Found",
            description=f"Collection '{collection_id}' does not exist.",
            http_status=404,
        )

    ingested_count = 0
    failure_count = 0
    objects = payload.objects or []

    for obj in objects:
        try:
            stix_id = obj.get("id") or f"{obj.get('type', 'indicator')}--{uuid.uuid4()}"
            stix_type = (obj.get("type") or "indicator").lower()

            name = obj.get("name")
            description = obj.get("description")
            pattern = obj.get("pattern")
            pattern_type = (obj.get("pattern_type") or "stix").lower()
            labels = obj.get("labels", [])
            confidence = obj.get("confidence", 75)
            revoked = bool(obj.get("revoked", False))
            source = obj.get("source") or "TAXII"

            timestamps = STIXValidator.validate_timestamps(
                valid_from=obj.get("valid_from"),
                valid_until=obj.get("valid_until"),
            )

            # Tenant isolation check
            stmt = select(StixObject).where(
                StixObject.stix_id == stix_id,
                StixObject.tenant_id == tenant_id,
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            # Prevent cross-tenant overwrite
            if not existing:
                collision_stmt = select(StixObject).where(
                    StixObject.stix_id == stix_id,
                    StixObject.tenant_id != tenant_id,
                )
                if (await db.execute(collision_stmt)).scalar_one_or_none():
                    tenant_prefix = tenant_id[:8]
                    if f"-{tenant_prefix}" not in stix_id:
                        stix_id = f"{stix_id}-{tenant_prefix}"

            if existing:
                existing.name = name
                existing.description = description
                existing.pattern = pattern
                existing.pattern_type = pattern_type
                existing.valid_from = timestamps["valid_from"]
                existing.valid_until = timestamps["valid_until"]
                existing.revoked = revoked
                existing.source = source
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
                    pattern_type=pattern_type,
                    valid_from=timestamps["valid_from"],
                    valid_until=timestamps["valid_until"],
                    revoked=revoked,
                    source=source,
                    labels=labels,
                    confidence=confidence,
                    raw_stix=obj,
                )
                db.add(new_stix)
            ingested_count += 1
        except Exception:
            failure_count += 1

    await db.commit()

    # Track TAXII status
    status_id = str(uuid.uuid4())
    status_payload = {
        "id": status_id,
        "status": "complete" if failure_count == 0 else "pending",
        "request_timestamp": datetime.utcnow().isoformat() + "Z",
        "total_count": len(objects),
        "success_count": ingested_count,
        "failure_count": failure_count,
        "pending_count": 0,
        "collection_id": collection_id,
        "bundle_id": payload.id,
    }
    _taxii_status_store[status_id] = status_payload

    return taxii_json_response(
        content={
            "status": "SUCCESS",
            "status_id": status_id,
            "collection_id": collection_id,
            "bundle_id": payload.id,
            "objects_ingested": ingested_count,
            "objects_failed": failure_count,
            "timestamp": datetime.utcnow().isoformat(),
        },
        status_code=status.HTTP_202_ACCEPTED,
        media_type=TAXII_MEDIA_TYPE,
    )


@router.get("/collections/{collection_id}/objects/")
async def get_taxii_objects(
    collection_id: str,
    match_type: Optional[str] = Query(None, alias="match[type]"),
    type_filter: Optional[str] = Query(None, alias="type"),
    match_id: Optional[str] = Query(None, alias="match[id]"),
    id_filter: Optional[str] = Query(None, alias="id"),
    added_after: Optional[str] = Query(None),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve STIX 2.1 objects from TAXII 2.1 collection with filtering and tenant isolation."""
    coll = AVAILABLE_COLLECTIONS.get(collection_id)
    if not coll:
        return taxii_error(
            title="Collection Not Found",
            description=f"Collection '{collection_id}' not found.",
            http_status=404,
        )

    stmt = select(StixObject).where(StixObject.tenant_id == tenant_id)

    # Filter by type
    effective_type = match_type or type_filter
    if effective_type:
        stmt = stmt.where(StixObject.type == effective_type.lower())

    # Filter by ID
    effective_id = match_id or id_filter
    if effective_id:
        stmt = stmt.where(StixObject.stix_id == effective_id)

    # Filter by added_after timestamp
    if added_after:
        try:
            dt_added_after = STIXValidator.parse_timestamp(added_after, "added_after")
            if dt_added_after:
                stmt = stmt.where(StixObject.created_at >= dt_added_after)
        except STIXValidationError:
            return taxii_error(
                title="Bad Request",
                description=f"Invalid added_after timestamp format: '{added_after}'",
                http_status=400,
            )

    result = await db.execute(stmt)
    stix_items = result.scalars().all()

    stix_objects = [item.raw_stix or {
        "id": item.stix_id,
        "type": item.type,
        "spec_version": item.spec_version,
        "name": item.name,
        "description": item.description,
        "pattern": item.pattern,
        "pattern_type": item.pattern_type,
        "valid_from": item.valid_from.isoformat() if item.valid_from else None,
        "valid_until": item.valid_until.isoformat() if item.valid_until else None,
        "revoked": item.revoked,
        "source": item.source,
        "labels": item.labels,
        "confidence": item.confidence,
    } for item in stix_items]

    return taxii_json_response(
        content={
            "type": "bundle",
            "id": f"bundle--{uuid.uuid4()}",
            "objects": stix_objects,
        },
        media_type=STIX_MEDIA_TYPE,
    )


@router.get("/collections/{collection_id}/objects/{object_id}/")
async def get_taxii_single_object(
    collection_id: str,
    object_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a single STIX 2.1 object by ID from a TAXII collection."""
    coll = AVAILABLE_COLLECTIONS.get(collection_id)
    if not coll:
        return taxii_error(
            title="Collection Not Found",
            description=f"Collection '{collection_id}' not found.",
            http_status=404,
        )

    stmt = select(StixObject).where(
        StixObject.stix_id == object_id,
        StixObject.tenant_id == tenant_id,
    )
    obj = (await db.execute(stmt)).scalar_one_or_none()

    if not obj:
        # Check tenant disambiguated ID
        disambiguated = f"{object_id}-{tenant_id[:8]}"
        stmt_dis = select(StixObject).where(
            StixObject.stix_id == disambiguated,
            StixObject.tenant_id == tenant_id,
        )
        obj = (await db.execute(stmt_dis)).scalar_one_or_none()

    if not obj:
        return taxii_error(
            title="Object Not Found",
            description=f"STIX object '{object_id}' not found in collection '{collection_id}'.",
            http_status=404,
        )

    stix_dict = obj.raw_stix or {
        "id": obj.stix_id,
        "type": obj.type,
        "spec_version": obj.spec_version,
        "name": obj.name,
        "description": obj.description,
        "pattern": obj.pattern,
        "pattern_type": obj.pattern_type,
        "valid_from": obj.valid_from.isoformat() if obj.valid_from else None,
        "valid_until": obj.valid_until.isoformat() if obj.valid_until else None,
        "revoked": obj.revoked,
        "source": obj.source,
        "labels": obj.labels,
        "confidence": obj.confidence,
    }

    return taxii_json_response(
        content={
            "type": "bundle",
            "id": f"bundle--{uuid.uuid4()}",
            "objects": [stix_dict],
        },
        media_type=STIX_MEDIA_TYPE,
    )
