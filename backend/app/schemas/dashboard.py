from datetime import datetime

from pydantic import BaseModel, Field


class RiskDistribution(BaseModel):
    LOW: int = 0
    MEDIUM: int = 0
    HIGH: int = 0
    CRITICAL: int = 0


class PriorityDistribution(BaseModel):
    P1: int = 0
    P2: int = 0
    P3: int = 0


class ComplaintTypeDistribution(BaseModel):
    product_quality: int = 0
    packaging_labeling: int = 0
    adverse_event: int = 0
    other: int = 0

class RecentComplaint(BaseModel):
    id: int
    complaint_number: str
    product_name: str | None = None
    complaint_type: str | None = None
    ai_risk_level: str | None = None
    priority: str | None = None
    status: str
    created_at: datetime


class DashboardSummary(BaseModel):
    total_complaints: int = 0
    pending_triage: int = 0
    under_investigation: int = 0
    qa_review: int = 0
    closed: int = 0

    risk_distribution: RiskDistribution = Field(
        default_factory=RiskDistribution
    )

    priority_distribution: PriorityDistribution = Field(
        default_factory=PriorityDistribution
    )

    complaint_type_distribution: ComplaintTypeDistribution = Field(
        default_factory=ComplaintTypeDistribution
    )