from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.graph import complaint_graph
from app.db.database import get_db
from app.models.complaint import Complaint
from app.schemas.complaint import (
    AIComplaintCreate,
    ComplaintCreate,
    ComplaintResponse,
    DuplicateCheckResponse,
)
from app.services.duplicate_detector import detect_duplicate


router = APIRouter(
    prefix="/api/complaints",
    tags=["Complaints"],
)


def generate_complaint_number(db: Session) -> str:
    count = db.query(Complaint).count() + 1
    return f"CMP-{count:05d}"


# ============================================================
# MANUAL COMPLAINT CREATION
# ============================================================

@router.post(
    "",
    response_model=ComplaintResponse,
)
def create_complaint(
    complaint_data: ComplaintCreate,
    db: Session = Depends(get_db),
):
    complaint = Complaint(
        complaint_number=generate_complaint_number(db),
        **complaint_data.model_dump(),
    )

    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    return complaint


# ============================================================
# AI-ASSISTED COMPLAINT CREATION
# ============================================================

@router.post(
    "/from-ai",
    response_model=ComplaintResponse,
)
def create_complaint_from_ai(
    request: AIComplaintCreate,
    db: Session = Depends(get_db),
):
    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Complaint text cannot be empty",
        )

    # --------------------------------------------------------
    # Run LangGraph AI pipeline
    # --------------------------------------------------------

    result = complaint_graph.invoke(
        {
            "input_text": request.text,
            "errors": [],
        }
    )

    complaint_data = result.get("complaint") or {}
    risk = result.get("risk_assessment") or {}
    priority_data = result.get("priority_assessment") or {}

    if not complaint_data:
        raise HTTPException(
            status_code=422,
            detail="AI could not extract complaint information",
        )

    # --------------------------------------------------------
    # Create complaint using AI-extracted information
    # --------------------------------------------------------

    complaint = Complaint(
        complaint_number=generate_complaint_number(db),

        complaint_source=complaint_data.get(
            "complaint_source"
        ),

        customer_name=complaint_data.get(
            "customer_name"
        ),

        product_name=complaint_data.get(
            "product_name"
        ),

        product_strength=complaint_data.get(
            "product_strength"
        ),

        batch_number=complaint_data.get(
            "batch_number"
        ),

        manufacturing_date=complaint_data.get(
            "manufacturing_date"
        ),

        expiry_date=complaint_data.get(
            "expiry_date"
        ),

        quantity_affected=complaint_data.get(
            "quantity_affected"
        ),

        quantity_unit=complaint_data.get(
            "quantity_unit"
        ),

        complaint_type=complaint_data.get(
            "complaint_type"
        ),

        complaint_date=complaint_data.get(
            "complaint_date"
        ),

        description=complaint_data.get(
            "description"
        ),

        # ----------------------------------------------------
        # AI assessment
        # ----------------------------------------------------

        initial_severity=risk.get(
            "severity"
        ),

        priority=priority_data.get(
            "priority"
        ),

        ai_confidence=risk.get(
            "confidence"
        ),

        ai_risk_level=risk.get(
            "risk_level"
        ),

        status="Pending Triage",
    )

    # --------------------------------------------------------
    # Save complaint
    # --------------------------------------------------------

    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    return complaint


# ============================================================
# DUPLICATE COMPLAINT DETECTION
# ============================================================

@router.post(
    "/check-duplicate",
    response_model=DuplicateCheckResponse,
)
def check_duplicate(
    complaint_data: ComplaintCreate,
    db: Session = Depends(get_db),
):
    existing_complaints = db.query(Complaint).all()

    new_complaint = complaint_data.model_dump()

    existing_data = [
        {
            "id": complaint.id,
            "complaint_number": complaint.complaint_number,
            "product_name": complaint.product_name,
            "batch_number": complaint.batch_number,
            "complaint_type": complaint.complaint_type,
            "customer_name": complaint.customer_name,
            "description": complaint.description,
        }
        for complaint in existing_complaints
    ]

    result = detect_duplicate(
        new_complaint=new_complaint,
        existing_complaints=existing_data,
    )

    return result


# ============================================================
# GET ALL COMPLAINTS
# ============================================================

@router.get(
    "",
    response_model=list[ComplaintResponse],
)
def get_complaints(
    db: Session = Depends(get_db),
):
    return (
        db.query(Complaint)
        .order_by(Complaint.created_at.desc())
        .all()
    )


# ============================================================
# GET COMPLAINT BY ID
# ============================================================

@router.get(
    "/{complaint_id}",
    response_model=ComplaintResponse,
)
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
):
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

    return complaint

