from datetime import date, datetime

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

    created_at: datetime
    updated_at: datetime