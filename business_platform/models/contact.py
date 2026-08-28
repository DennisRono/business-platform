from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from business_platform.models.base import BaseModel
from business_platform.utils.enums import ContactType


class Contact(BaseModel):
    """Represents a CRM-style contact, optionally linked to a Business/Person."""
    __tablename__ = "contacts"

    business_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=True, index=True,
    )
    person_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("people.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    contact_type: Mapped[ContactType] = mapped_column(
        String(20), default=ContactType.PRIMARY, nullable=False, index=True
    )
    first_name: Mapped[str] = mapped_column(String(150), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    job_title: Mapped[str | None] = mapped_column(String(150), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    business: Mapped["Business | None"] = relationship(back_populates="contacts")
    person: Mapped["Person | None"] = relationship()
