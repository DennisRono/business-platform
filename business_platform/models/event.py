from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from business_platform.models.base import BaseModel
from business_platform.utils.enums import EventStatus, EventType


class Event(BaseModel):
    """Represents a dated event tied to a Business."""
    __tablename__ = "events"

    business_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    event_type: Mapped[EventType] = mapped_column(String(30), nullable=False, index=True)
    status: Mapped[EventStatus] = mapped_column(
        String(20), default=EventStatus.SCHEDULED, nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recurrence_rule: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="RFC 5545 RRULE string, if is_recurring"
    )
    reminder_days_before: Mapped[int | None] = mapped_column(Integer, nullable=True)
    related_document_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )

    business: Mapped["Business"] = relationship(back_populates="events")
    related_document: Mapped["Document | None"] = relationship()
