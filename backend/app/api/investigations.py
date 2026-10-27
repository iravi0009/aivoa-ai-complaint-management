from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.complaint import Complaint
from app.models.investigation import Investigation

from app.schemas.investigation import (
    InvestigationCreate,
    InvestigationResponse,
    InvestigationUpdate,
    RootCauseRecommendation,
)

from app.schemas.capa import CAPARecommendation

from app.services.ai_service import (
    recommend_capa,
    recommend_root_causes,
)


router = APIRouter(
    prefix="/api/complaints",
    tags=["Investigations"],
)


# ============================================================
# CREATE INVESTIGATION
# ============================================================

@router.post(
    "/{complaint_id}/investigation",
    response_model=InvestigationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_investigation(
    complaint_id: int,
    investigation_data: InvestigationCreate,
    db: Session = Depends(get_db),
):
    # Verify complaint exists.
    complaint = (
        db.query(Complaint)
        .filter(Complaint.id == complaint_id)
        .first()
    )

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found",
        )

    # Prevent duplicate investigation records.
    existing = (
        db.query(Investigation)
        .filter(Investigation.complaint_id == complaint_id)
        .first()
    )

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Investigation already exists for this complaint",
        )

    investigation = Investigation(
        complaint_id=complaint_id,
        **investigation_data.model_dump(),
    )

    db.add(investigation)

    # Complaint enters investigation workflow.
    complaint.status = "Under Investigation"

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Investigation already exists for this complaint",
        )

    db.refresh(investigation)

    return investigation


# ============================================================
# GET INVESTIGATION
# ============================================================

@router.get(
    "/{complaint_id}/investigation",
    response_model=InvestigationResponse,
)
def get_investigation(
    complaint_id: int,
    db: Session = Depends(get_db),
):
    investigation = (
        db.query(Investigation)
        .filter(Investigation.complaint_id == complaint_id)
        .first()
    )

    if investigation is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    return investigation


# ============================================================
# ROOT CAUSE RECOMMENDATION
# ============================================================

@router.post(
    "/{complaint_id}/investigation/root-cause-recommendation",
    response_model=RootCauseRecommendation,
)
def recommend_complaint_root_causes(
    complaint_id: int,
    db: Session = Depends(get_db),
):
    # Verify complaint exists.
    complaint = (
        db.query(Complaint)
        .filter(Complaint.id == complaint_id)
        .first()
    )

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found",
        )

    # Root-cause recommendations require an investigation.
    investigation = (
        db.query(Investigation)
        .filter(Investigation.complaint_id == complaint_id)
        .first()
    )

    if investigation is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    # Build controlled context for the AI.
    complaint_text = f"""
Customer: {complaint.customer_name or "Not provided"}
Product: {complaint.product_name or "Not provided"}
Strength: {complaint.product_strength or "Not provided"}
Batch: {complaint.batch_number or "Not provided"}
Complaint Type: {complaint.complaint_type or "Not provided"}
Description: {complaint.description or "Not provided"}
Severity: {complaint.initial_severity or "Not provided"}
Risk Level: {complaint.ai_risk_level or "Not provided"}
Priority: {complaint.priority or "Not provided"}

Investigation Summary:
{investigation.investigation_summary or "Not provided"}

Impact Assessment:
{investigation.impact_assessment or "Not provided"}
""".strip()

    try:
        recommendation = recommend_root_causes(
            complaint_text
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Root cause recommendation failed: {exc}",
        ) from exc

    return recommendation


# ============================================================
# CAPA RECOMMENDATION
# ============================================================

@router.post(
    "/{complaint_id}/investigation/capa-recommendation",
    response_model=CAPARecommendation,
)
def recommend_complaint_capa(
    complaint_id: int,
    db: Session = Depends(get_db),
):
    # Verify complaint exists.
    complaint = (
        db.query(Complaint)
        .filter(Complaint.id == complaint_id)
        .first()
    )

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found",
        )

    # CAPA recommendations require an investigation.
    investigation = (
        db.query(Investigation)
        .filter(Investigation.complaint_id == complaint_id)
        .first()
    )

    if investigation is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    # Build controlled context for the AI.
    complaint_text = f"""
Customer: {complaint.customer_name or "Not provided"}
Product: {complaint.product_name or "Not provided"}
Strength: {complaint.product_strength or "Not provided"}
Batch: {complaint.batch_number or "Not provided"}
Complaint Type: {complaint.complaint_type or "Not provided"}
Description: {complaint.description or "Not provided"}
Severity: {complaint.initial_severity or "Not provided"}
Risk Level: {complaint.ai_risk_level or "Not provided"}
Priority: {complaint.priority or "Not provided"}

Investigation Summary:
{investigation.investigation_summary or "Not provided"}

Impact Assessment:
{investigation.impact_assessment or "Not provided"}

Root Cause:
{investigation.root_cause or "No confirmed root cause"}
""".strip()

    try:
        recommendation = recommend_capa(
            complaint_text
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"CAPA recommendation failed: {exc}",
        ) from exc

    return recommendation


# ============================================================
# UPDATE INVESTIGATION
# ============================================================

@router.patch(
    "/{complaint_id}/investigation",
    response_model=InvestigationResponse,
)
def update_investigation(
    complaint_id: int,
    investigation_data: InvestigationUpdate,
    db: Session = Depends(get_db),
):
    # Fetch investigation.
    investigation = (
        db.query(Investigation)
        .filter(Investigation.complaint_id == complaint_id)
        .first()
    )

    if investigation is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    # Fetch parent complaint.
    complaint = (
        db.query(Complaint)
        .filter(Complaint.id == complaint_id)
        .first()
    )

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found",
        )

    # Validate investigation lifecycle transitions.
    current_status = investigation.status
    requested_status = investigation_data.status

    if requested_status is not None:
        requested_status = requested_status.value

        allowed_transitions = {
            "OPEN": {
                "OPEN",
                "UNDER_INVESTIGATION",
            },
            "UNDER_INVESTIGATION": {
                "UNDER_INVESTIGATION",
                "COMPLETED",
            },
            "COMPLETED": {
                "COMPLETED",
            },
        }

        if requested_status not in allowed_transitions.get(
            current_status,
            set(),
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid investigation status transition: "
                    f"{current_status} -> {requested_status}"
                ),
            )

    # Apply investigation updates.
    update_data = investigation_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(
            investigation,
            field,
            value.value if hasattr(value, "value") else value,
        )

    # Synchronize complaint lifecycle.
    if investigation.status == "UNDER_INVESTIGATION":
        complaint.status = "Under Investigation"

    elif investigation.status == "COMPLETED":
        complaint.status = "QA Review"

    elif investigation.status == "OPEN":
        complaint.status = "Pending Triage"

    db.commit()
    db.refresh(investigation)

    return investigation