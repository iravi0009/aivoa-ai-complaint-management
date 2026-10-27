from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class InvestigationStatus(str, Enum):
    OPEN = "OPEN"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    COMPLETED = "COMPLETED"


class InvestigationCreate(BaseModel):
    investigation_summary: str | None = None
    impact_assessment: str | None = None
    root_cause: str | None = None
    conclusion: str | None = None


class InvestigationUpdate(BaseModel):
    status: InvestigationStatus | None = None
    investigation_summary: str | None = None
    impact_assessment: str | None = None
    root_cause: str | None = None
    conclusion: str | None = None


class InvestigationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    complaint_id: int
    status: InvestigationStatus

    investigation_summary: str | None
    impact_assessment: str | None
    root_cause: str | None
    conclusion: str | None

    created_at: datetime
    updated_at: datetime


# ============================================================
# ROOT CAUSE RECOMMENDATION
# ============================================================

class RootCauseRecommendationRequest(BaseModel):
    """Input used to generate AI root-cause recommendations."""

    complaint_id: int


class RootCauseRecommendation(BaseModel):
    """AI-generated investigation guidance, not a confirmed root cause."""

    recommendations: list[str]
    rationale: str
    disclaimer: str = (
        "AI-generated investigation guidance. "
        "Root cause must be confirmed by authorized QA/investigation personnel."
    )