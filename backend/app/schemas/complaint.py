from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ComplaintBase(BaseModel):
    complaint_source: str | None = None
    customer_name: str | None = None

    product_name: str | None = None
    product_strength: str | None = None
    batch_number: str | None = None

    manufacturing_date: date | None = None
    expiry_date: date | None = None

    quantity_affected: float | None = None
    quantity_unit: str | None = None

    complaint_type: str | None = None
    complaint_date: date | None = None

    description: str | None = None

    initial_severity: str | None = None
    priority: str | None = None

    ai_confidence: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )


class ComplaintCreate(ComplaintBase):
    pass


class ComplaintResponse(ComplaintBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    complaint_number: str
    status: str

    ai_risk_level: "RiskLevel | None" = None

    created_at: datetime
    updated_at: datetime


# ============================================================
# AI COMPLAINT CREATION REQUEST
# ============================================================

class AIComplaintCreate(BaseModel):
    """Raw complaint text submitted for AI-assisted logging."""

    text: str


# ============================================================
# AI RESPONSE SCHEMAS
# ============================================================

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Severity(str, Enum):
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"


class Priority(str, Enum):
    P3 = "P3"
    P2 = "P2"
    P1 = "P1"


class AIComplaintExtraction(BaseModel):
    """Structured complaint data extracted by the AI."""

    complaint_source: str | None = None
    customer_name: str | None = None

    product_name: str | None = None
    product_strength: str | None = None
    batch_number: str | None = None

    manufacturing_date: date | None = None
    expiry_date: date | None = None

    quantity_affected: float | None = None
    quantity_unit: str | None = None

    complaint_type: str | None = None
    complaint_date: date | None = None

    description: str | None = None


class AICompleteness(BaseModel):
    """Completeness evaluation of an extracted complaint."""

    is_complete: bool
    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class AIRiskAssessment(BaseModel):
    """Explainable AI/rule-based risk assessment."""

    risk_level: RiskLevel
    severity: Severity

    confidence: float = Field(
        ge=0,
        le=1,
    )

    reasoning: str

    score: int = Field(
        ge=0,
    )

    factors: list[str] = Field(
        default_factory=list,
    )


class AIPriorityAssessment(BaseModel):
    """Complaint priority recommendation."""

    priority: Priority
    reasoning: str


class AIAnalysisResponse(BaseModel):
    """Validated response returned by the complete AI pipeline."""

    complaint: AIComplaintExtraction
    completeness: AICompleteness
    risk_assessment: AIRiskAssessment
    priority_assessment: AIPriorityAssessment

class DuplicateCheckResponse(BaseModel):
    is_duplicate: bool
    duplicate_status: str
    matches: list[dict] = Field(default_factory=list)