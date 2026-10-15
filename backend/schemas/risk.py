from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


RiskTreatment = Literal["Mitigate", "Accept", "Transfer", "Avoid"]


class RiskCreate(BaseModel):
    """Client-supplied fields for a new risk."""

    model_config = ConfigDict(extra="forbid")

    description: str = Field(..., min_length=1)
    owner: str = Field(..., min_length=1, max_length=255)
    likelihood: int = Field(..., ge=1, le=5)
    impact: int = Field(..., ge=1, le=5)
    treatment: RiskTreatment


class RiskResponse(BaseModel):
    """Risk register entry returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    risk_id: int
    tenant_id: int
    description: str
    owner: str
    likelihood: int
    impact: int
    inherent_risk_score: int
    treatment: RiskTreatment
    status: Literal["Open", "Closed"]
    closure_reason: str | None
    closed_at: datetime | None
    closed_by: str | None
    ciso_signoff_by: str | None
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def risk_level(self) -> Literal["Low", "Medium", "High", "Critical"]:
        """Return the ISO register's score band."""
        if self.inherent_risk_score <= 4:
            return "Low"
        if self.inherent_risk_score <= 9:
            return "Medium"
        if self.inherent_risk_score <= 15:
            return "High"
        return "Critical"


class RiskCloseRequest(BaseModel):
    """Required closure reason and optional sign-off identity claim."""

    model_config = ConfigDict(extra="forbid")

    closure_reason: str = Field(..., min_length=1)
    ciso_signoff: str | None = None


class DPDPClockCreate(BaseModel):
    """Client-supplied details for starting a DPDP breach clock."""

    model_config = ConfigDict(extra="forbid")

    breach_description: str = Field(..., min_length=1)
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("detected_at")
    @classmethod
    def require_timezone_aware_detected_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("detected_at must include a timezone")
        return value.astimezone(timezone.utc)


class DPDPClockResponse(BaseModel):
    """A breach clock with its deadline state computed at read time."""

    id: int
    tenant_id: int
    breach_description: str
    detected_at: datetime
    deadline_at: datetime
    status: Literal["Open", "Notified", "Overdue"]
    hours_remaining: float
    is_overdue: bool
    notified_at: datetime | None
