from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from business_platform.models.base import BaseModel


class Person(BaseModel):
    """
    Represents a natural person. Created either standalone or scoped to
    a business via POST /business/{business_id}/people, which records
    that business as the person's `primary_business_id`.
    """
    __tablename__ = "people"

    primary_business_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="SET NULL"),
        nullable=True, index=True,
        comment="Business scope the person was originally created under",
    )
    first_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    address_line_1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(30), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)

    primary_business: Mapped["Business | None"] = relationship(foreign_keys=[primary_business_id])
    ownership_records: Mapped[list["OwnershipRecord"]] = relationship(back_populates="person")
    leadership_records: Mapped[list["Leader"]] = relationship(back_populates="person")
    employment_records: Mapped[list["Employee"]] = relationship(back_populates="person")
