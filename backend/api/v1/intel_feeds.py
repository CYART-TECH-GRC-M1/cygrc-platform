from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.services.intel_integrations import IntelIntegrationService

router = APIRouter()


class MispSyncRequest(BaseModel):
    misp_payload: Dict[str, Any]


class OpenCTIGraphQLRequest(BaseModel):
    graphql_data: Dict[str, Any]


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
        db=db
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
        db=db
    )
    return result
