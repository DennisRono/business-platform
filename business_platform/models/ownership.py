from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from business_platform.models.base import BaseModel
from business_platform.utils.enums import OwnershipStatus, OwnershipType


class OwnershipRecord(BaseModel):
    """Represents a Person's ownership stake in a Business."""
    __tablename__ = "ownership_records"

    business_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    person_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("people.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    ownership_type: Mapped[OwnershipType] = mapped_column(String(30), nullable=False)
    status: Mapped[OwnershipStatus] = mapped_column(
        String(20), default=OwnershipStatus.PENDING, nullable=False, index=True
    )
    percentage: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    shares_count: Mapped[int | None] = mapped_column(nullable=True)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    business: Mapped["Business"] = relationship(back_populates="owners")
    person: Mapped["Person"] = relationship(back_populates="ownership_records")
    transitions: Mapped[list["OwnershipTransition"]] = relationship(
        back_populates="ownership_record", cascade="all, delete-orphan"
    )


class OwnershipTransition(BaseModel):
    """
    Append-only log of every status change made to an OwnershipRecord.
    Written by the PATCH .../owners/{ownership_record_id} endpoint.
    """
    __tablename__ = "ownership_transitions"

    ownership_record_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ownership_records.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    from_status: Mapped[OwnershipStatus | None] = mapped_column(String(20), nullable=True)
    to_status: Mapped[OwnershipStatus] = mapped_column(String(20), nullable=False)
    transitioned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    transitioned_by_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    ownership_record: Mapped["OwnershipRecord"] = relationship(back_populates="transitions")
