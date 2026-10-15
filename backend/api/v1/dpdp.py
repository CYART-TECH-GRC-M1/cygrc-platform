from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, status

from backend.api.v1.risks import AuthContext, get_auth_context
from backend.models.risk import DPDPBreachClock
from backend.schemas.risk import DPDPClockCreate, DPDPClockResponse

BREACH_NOTIFICATION_HOURS = 72

router = APIRouter(prefix="/api/v1", tags=["dpdp"])

_clocks: dict[int, DPDPBreachClock] = {}
_next_clock_id = 1


def calculate_deadline(detected_at: datetime) -> datetime:
    """Return the statutory 72-hour notification deadline."""
    return detected_at + timedelta(hours=BREACH_NOTIFICATION_HOURS)


def build_clock_response(
    clock: DPDPBreachClock,
    now: datetime | None = None,
) -> DPDPClockResponse:
    """Build a clock response with remaining time evaluated at request time."""
    current_time = now or datetime.now(timezone.utc)
    hours_remaining = (clock.deadline_at - current_time).total_seconds() / 3600
    is_overdue = current_time > clock.deadline_at and clock.notified_at is None
    response_status = "Overdue" if is_overdue else clock.status
    return DPDPClockResponse(
        id=clock.id,
        tenant_id=clock.tenant_id,
        breach_description=clock.breach_description,
        detected_at=clock.detected_at,
        deadline_at=clock.deadline_at,
        status=response_status,
        hours_remaining=hours_remaining,
        is_overdue=is_overdue,
        notified_at=clock.notified_at,
    )


@router.post(
    "/dpdp/breach-clock",
    response_model=DPDPClockResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_breach_clock(
    payload: DPDPClockCreate,
    auth: AuthContext = Depends(get_auth_context),
) -> DPDPClockResponse:
    """Start a tenant breach clock with a fixed 72-hour deadline."""
    global _next_clock_id

    now = datetime.now(timezone.utc)
    clock = DPDPBreachClock(
        id=_next_clock_id,
        tenant_id=auth.tenant_id,
        breach_description=payload.breach_description,
        detected_at=payload.detected_at,
        deadline_at=calculate_deadline(payload.detected_at),
        status="Open",
        notified_at=None,
        created_at=now,
    )
    _clocks[clock.id] = clock
    _next_clock_id += 1
    return build_clock_response(clock, now=now)


@router.get("/dpdp/breach-clock", response_model=list[DPDPClockResponse])
def get_breach_clocks(
    auth: AuthContext = Depends(get_auth_context),
) -> list[DPDPClockResponse]:
    """List breach clocks for the authenticated tenant only."""
    now = datetime.now(timezone.utc)
    return [
        build_clock_response(clock, now=now)
        for clock in _clocks.values()
        if clock.tenant_id == auth.tenant_id
    ]
