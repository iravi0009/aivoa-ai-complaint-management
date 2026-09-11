from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.complaint import Complaint
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintResponse,
)


router = APIRouter(
    prefix="/api/complaints",
    tags=["Complaints"],
)


def generate_complaint_number(db: Session) -> str:
    count = db.query(Complaint).count() + 1
    return f"CMP-{count:05d}"


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