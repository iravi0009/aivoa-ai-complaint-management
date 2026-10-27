from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.complaint import Complaint
from app.schemas.dashboard import (
    DashboardSummary,
    RecentComplaint,
)


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

@router.get(
    "/summary",
    response_model=DashboardSummary,
)
def get_dashboard_summary(
    db: Session = Depends(get_db),
):
    complaints = db.query(Complaint).all()

    summary = DashboardSummary(
        total_complaints=len(complaints),
    )

    for complaint in complaints:
        status = (complaint.status or "").strip().lower()
        risk = (complaint.ai_risk_level or "").strip().upper()
        priority = (complaint.priority or "").strip().upper()
        complaint_type = (
            complaint.complaint_type or ""
        ).strip().lower()

        # ----------------------------------------------------
        # STATUS DISTRIBUTION
        # ----------------------------------------------------

        if status == "pending triage":
            summary.pending_triage += 1

        elif status == "under investigation":
            summary.under_investigation += 1

        elif status == "qa review":
            summary.qa_review += 1

        elif status == "closed":
            summary.closed += 1

        # ----------------------------------------------------
        # RISK DISTRIBUTION
        # ----------------------------------------------------

        if risk == "LOW":
            summary.risk_distribution.LOW += 1

        elif risk == "MEDIUM":
            summary.risk_distribution.MEDIUM += 1

        elif risk == "HIGH":
            summary.risk_distribution.HIGH += 1

        elif risk == "CRITICAL":
            summary.risk_distribution.CRITICAL += 1

        # ----------------------------------------------------
        # PRIORITY DISTRIBUTION
        # ----------------------------------------------------

        if priority == "P1":
            summary.priority_distribution.P1 += 1

        elif priority == "P2":
            summary.priority_distribution.P2 += 1

        elif priority == "P3":
            summary.priority_distribution.P3 += 1

        # ----------------------------------------------------
        # COMPLAINT TYPE DISTRIBUTION
        # ----------------------------------------------------

        if complaint_type == "product quality":
            summary.complaint_type_distribution.product_quality += 1

        elif complaint_type == "packaging/labeling":
            summary.complaint_type_distribution.packaging_labeling += 1

        elif complaint_type == "adverse event":
            summary.complaint_type_distribution.adverse_event += 1

        else:
            summary.complaint_type_distribution.other += 1

    return summary


# ============================================================
# RECENT COMPLAINTS
# ============================================================

@router.get(
    "/recent",
    response_model=list[RecentComplaint],
)
def get_recent_complaints(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    limit = max(1, min(limit, 50))

    complaints = (
        db.query(Complaint)
        .order_by(Complaint.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        RecentComplaint(
            id=complaint.id,
            complaint_number=complaint.complaint_number,
            product_name=complaint.product_name,
            complaint_type=complaint.complaint_type,
            ai_risk_level=complaint.ai_risk_level,
            priority=complaint.priority,
            status=complaint.status,
            created_at=complaint.created_at,
        )
        for complaint in complaints
    ]