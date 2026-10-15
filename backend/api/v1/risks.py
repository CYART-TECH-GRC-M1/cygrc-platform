from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from backend.models.risk import Risk
from backend.schemas.risk import RiskCloseRequest, RiskCreate, RiskResponse

router = APIRouter(prefix="/api/v1", tags=["risks"])

_risks: dict[int, Risk] = {}
_next_risk_id = 1


@dataclass(frozen=True)
class AuthContext:
    """Trusted identity context attached by the application's auth middleware."""

    tenant_id: int
    user_id: str
    roles: frozenset[str]


def _context_value(context: Any, key: str, default: Any = None) -> Any:
    if isinstance(context, Mapping):
        return context.get(key, default)
    return getattr(context, key, default)


def get_auth_context(request: Request) -> AuthContext:
    """Read trusted principal data from request state; never from client fields."""
    raw_context = getattr(request.state, "auth_context", None)
    if raw_context is None:
        raise HTTPException(status_code=401, detail="Authenticated tenant context is required")

    tenant_id = _context_value(raw_context, "tenant_id")
    user_id = _context_value(raw_context, "user_id", _context_value(raw_context, "sub"))
    roles = _context_value(raw_context, "roles", ())
    if isinstance(roles, str):
        roles = (roles,)
    try:
        tenant_id = int(tenant_id)
    except (TypeError, ValueError):
        tenant_id = 0
    if tenant_id < 1 or not user_id:
        raise HTTPException(status_code=401, detail="Authenticated tenant context is invalid")
    return AuthContext(
        tenant_id=tenant_id,
        user_id=str(user_id),
        roles=frozenset(str(role).casefold() for role in roles),
    )


def calculate_risk_score(likelihood: int, impact: int) -> int:
    """Calculate the inherent risk score from the server-validated factors."""
    return likelihood * impact


def _require_ciso_signoff(score: int, auth: AuthContext) -> str | None:
    """Return the sign-off identity or reject a high-risk closure."""
    if score < 16:
        return None
    if "ciso" not in auth.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CISO role sign-off is required before closing a risk with score 16 or higher.",
        )
    return auth.user_id


@router.get("/risks", response_model=list[RiskResponse])
def list_risks(
    status_filter: str | None = Query(default=None, alias="status", pattern="^(Open|Closed)$"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    auth: AuthContext = Depends(get_auth_context),
) -> list[RiskResponse]:
    """List risks belonging only to the authenticated tenant."""
    tenant_risks = [risk for risk in _risks.values() if risk.tenant_id == auth.tenant_id]
    if status_filter is not None:
        tenant_risks = [risk for risk in tenant_risks if risk.status == status_filter]
    return [RiskResponse.model_validate(risk) for risk in tenant_risks[skip : skip + limit]]


@router.post("/risks", response_model=RiskResponse, status_code=status.HTTP_201_CREATED)
def create_risk(
    payload: RiskCreate,
    auth: AuthContext = Depends(get_auth_context),
) -> RiskResponse:
    """Create a risk and compute its score on the server."""
    global _next_risk_id

    now = datetime.now(timezone.utc)
    risk = Risk(
        risk_id=_next_risk_id,
        tenant_id=auth.tenant_id,
        description=payload.description,
        owner=payload.owner,
        likelihood=payload.likelihood,
        impact=payload.impact,
        inherent_risk_score=calculate_risk_score(payload.likelihood, payload.impact),
        treatment=payload.treatment,
        status="Open",
        created_at=now,
        updated_at=now,
    )
    _risks[risk.risk_id] = risk
    _next_risk_id += 1
    return RiskResponse.model_validate(risk)


@router.post("/risks/{risk_id}/close", response_model=RiskResponse)
def close_risk(
    risk_id: int,
    payload: RiskCloseRequest,
    auth: AuthContext = Depends(get_auth_context),
) -> RiskResponse:
    """Close a tenant risk, requiring a CISO principal for scores >= 16."""
    risk = _risks.get(risk_id)
    if risk is None or risk.tenant_id != auth.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk not found")
    if risk.status == "Closed":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Risk is already closed")

    signoff_by = _require_ciso_signoff(risk.inherent_risk_score, auth)
    now = datetime.now(timezone.utc)
    risk.status = "Closed"
    risk.closure_reason = payload.closure_reason
    risk.closed_at = now
    risk.closed_by = auth.user_id
    risk.ciso_signoff_by = signoff_by
    risk.updated_at = now
    return RiskResponse.model_validate(risk)
