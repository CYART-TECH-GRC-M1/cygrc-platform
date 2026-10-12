from typing import Dict, Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id, require_permission
from backend.core.permissions import Permission
from backend.services.intel_integrations import IntelIntegrationService

router = APIRouter()


class MispSyncRequest(BaseModel):
    misp_payload: Dict[str, Any]


class OpenCTIGraphQLRequest(BaseModel):
    graphql_data: Dict[str, Any]


@router.post("/misp/sync", status_code=status.HTTP_200_OK)
async def sync_misp_event(
    payload: MispSyncRequest,
    _permission: Dict[str, Any] = Depends(
        require_permission(Permission.INTEL_INGEST)
    ),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Ingest MISP event data with permission checks."""
    return await IntelIntegrationService.sync_misp_events(
        misp_payload=payload.misp_payload,
        tenant_id=tenant_id,
        db=db,
    )


@router.post("/opencti/query", status_code=status.HTTP_200_OK)
async def sync_opencti_graphql(
    payload: OpenCTIGraphQLRequest,
    _permission: Dict[str, Any] = Depends(
        require_permission(Permission.INTEL_INGEST)
    ),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Ingest OpenCTI data with permission checks."""
    return await IntelIntegrationService.sync_opencti_graphql(
        graphql_data=payload.graphql_data,
        tenant_id=tenant_id,
        db=db,
    )
