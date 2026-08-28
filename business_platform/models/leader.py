from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from business_platform.models.base import BaseModel
from business_platform.utils.enums import LeaderStatus, LeaderTitle


class Leader(BaseModel):
    """Represents a Person holding an officer/director title at a Business."""
    __tablename__ = "leaders"

    business_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    person_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("people.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    title: Mapped[LeaderTitle] = mapped_column(String(30), nullable=False, index=True)
    status: Mapped[LeaderStatus] = mapped_column(
        String(20), default=LeaderStatus.ACTIVE, nullable=False, index=True
    )
    appointed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    resigned_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_signatory: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    voting_rights: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    business: Mapped["Business"] = relationship(back_populates="leaders")
    person: Mapped["Person"] = relationship(back_populates="leadership_records")
