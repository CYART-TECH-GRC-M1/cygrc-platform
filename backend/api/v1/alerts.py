import asyncio
import json
from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.models.alert import Alert, AlertSeverity, AlertStatus
from backend.services.sigma_parser import SigmaParserService
from backend.services.alert_enrichment import AlertEnrichmentService
from backend.services.siem_control_bridge import SIEMControlBridgeService

router = APIRouter()


class AlertCreate(BaseModel):
    title: str
    source: str = "Wazuh"
    severity: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    description: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None


class AlertUpdate(BaseModel):
    status: Optional[str] = None  # NEW, TRIAGED, IN_PROGRESS, CLOSED, ESCALATED
    severity: Optional[str] = None
    description: Optional[str] = None


class ControlFeedRequest(BaseModel):
    alert_id: str
    title: str
    severity: str
    control_id: Optional[str] = "A.5.1"


class AlertResponse(BaseModel):
    alert_id: str
    tenant_id: Optional[str] = None
    title: str
    source: str
    severity: str
    status: str
    description: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SigmaConvertRequest(BaseModel):
    sigma_yaml: str
    rule_id_start: Optional[int] = 100001


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def ingest_alert(
    payload: AlertCreate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    alert = Alert(
        tenant_id=tenant_id,
        title=payload.title,
        source=payload.source,
        severity=payload.severity.upper(),
        status=AlertStatus.NEW.value,
        description=payload.description,
        raw_payload=payload.raw_payload or {},
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


@router.post("/wazuh/webhook", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def wazuh_alert_listener(
    raw_event: Dict[str, Any],
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    rule = raw_event.get("rule", {})
    agent = raw_event.get("agent", {})

    level = rule.get("level", 5)
    description = rule.get("description") or raw_event.get("full_log") or "Wazuh Alert"

    if level >= 12:
        severity = "CRITICAL"
    elif level >= 8:
        severity = "HIGH"
    elif level >= 4:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    agent_name = agent.get("name", "unknown-agent")
    title = f"Wazuh [{agent_name}]: {rule.get('description', 'Security Event')}"

    alert = Alert(
        tenant_id=tenant_id,
        title=title,
        source="Wazuh SIEM Listener",
        severity=severity,
        status=AlertStatus.NEW.value,
        description=description,
        raw_payload=raw_event,
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


@router.post("/feed-control-evidence")
async def feed_siem_alert_to_control_status_engine(
    payload: ControlFeedRequest,
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Feed Module 2 SIEM alert signals directly to Module 1 Control Status Engine as automated evidence."""
    result = SIEMControlBridgeService.feed_siem_alerts_to_control_engine(
        alert_id=payload.alert_id,
        title=payload.title,
        severity=payload.severity,
        tenant_id=tenant_id,
        control_id=payload.control_id or "A.5.1"
    )
    return result


@router.get("/stream")
async def stream_realtime_alerts(
    tenant_id: str = Depends(get_current_tenant_id),
):
    async def event_generator():
        for i in range(5):
            data = {
                "event": "alert_heartbeat",
                "tenant_id": tenant_id,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "STREAMING_ACTIVE"
            }
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/sigma/convert")
async def convert_sigma_rule(payload: SigmaConvertRequest):
    result = SigmaParserService.parse_sigma_to_wazuh(
        sigma_yaml_text=payload.sigma_yaml,
        rule_id_start=payload.rule_id_start or 100001
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/{alert_id}/enrich")
async def enrich_alert_with_stix(
    alert_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    result = await AlertEnrichmentService.enrich_alert_with_stix(
        alert_id=alert_id,
        tenant_id=tenant_id,
        db=db
    )
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result


@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = Query(None),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Alert).where(Alert.tenant_id == tenant_id)
    if status_filter:
        stmt = stmt.where(Alert.status == status_filter.upper())
    if severity:
        stmt = stmt.where(Alert.severity == severity.upper())
    stmt = stmt.order_by(Alert.created_at.desc())

    result = await db.execute(stmt)
    alerts = result.scalars().all()
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Alert).where(Alert.alert_id == alert_id, Alert.tenant_id == tenant_id)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    payload: AlertUpdate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Alert).where(Alert.alert_id == alert_id, Alert.tenant_id == tenant_id)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if payload.status:
        alert.status = payload.status.upper()
    if payload.severity:
        alert.severity = payload.severity.upper()
    if payload.description is not None:
        alert.description = payload.description

    alert.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(alert)
    return alert
