from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.services.intel_integrations import IntelIntegrationService
from backend.services.misp_client import MISPClient
from backend.services.opencti_client import OpenCTIClient

router = APIRouter()


class MispSyncRequest(BaseModel):
    misp_payload: Dict[str, Any]


class OpenCTIGraphQLRequest(BaseModel):
    graphql_data: Dict[str, Any]


class MispFetchRequest(BaseModel):
    page: Optional[int] = 1
    limit: Optional[int] = 50
    filters: Optional[Dict[str, Any]] = None


class OpenCTIFetchRequest(BaseModel):
    first: Optional[int] = 50
    after: Optional[str] = None


@router.get("/status", status_code=status.HTTP_200_OK)
async def get_provider_status():
    """Returns configuration status for MISP and OpenCTI providers without exposing secrets."""
    return {
        "misp": {
            "configured": MISPClient.is_configured(),
        },
        "opencti": {
            "configured": OpenCTIClient.is_configured(),
        },
    }


@router.post("/misp/sync", status_code=status.HTTP_200_OK)
async def sync_misp_event(
    payload: MispSyncRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Ingest PyMISP event attributes and convert into STIX 2.1 Indicators."""
    result = await IntelIntegrationService.sync_misp_events(
        misp_payload=payload.misp_payload,
        tenant_id=tenant_id,
        db=db,
    )
    return result


@router.post("/misp/fetch", status_code=status.HTTP_200_OK)
async def fetch_misp_live(
    payload: Optional[MispFetchRequest] = None,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Fetch live threat events from configured MISP instance and sync into tenant STIX indicators."""
    req = payload or MispFetchRequest()
    result = await IntelIntegrationService.sync_misp_live(
        tenant_id=tenant_id,
        db=db,
        page=req.page or 1,
        limit=req.limit or 50,
        filters=req.filters,
    )
    return result


@router.post("/opencti/query", status_code=status.HTTP_200_OK)
async def sync_opencti_graphql(
    payload: OpenCTIGraphQLRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Query OpenCTI GraphQL client payload and store STIX entities."""
    result = await IntelIntegrationService.sync_opencti_graphql(
        graphql_data=payload.graphql_data,
        tenant_id=tenant_id,
        db=db,
    )
    return result


@router.post("/opencti/fetch", status_code=status.HTTP_200_OK)
async def fetch_opencti_live(
    payload: Optional[OpenCTIFetchRequest] = None,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Fetch live indicators from configured OpenCTI GraphQL instance and store with tenant isolation."""
    req = payload or OpenCTIFetchRequest()
    result = await IntelIntegrationService.sync_opencti_live(
        tenant_id=tenant_id,
        db=db,
        first=req.first or 50,
        after=req.after,
    )
    return result
