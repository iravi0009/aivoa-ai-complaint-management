from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    complaint_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
    )

    complaint_source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    customer_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    product_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    product_strength: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    batch_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    manufacturing_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    expiry_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    quantity_affected: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    quantity_unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    complaint_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    complaint_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    initial_severity: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    priority: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="Pending Triage",
    )

    ai_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )