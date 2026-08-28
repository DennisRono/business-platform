from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from business_platform.models.base import BaseModel
from business_platform.utils.enums import TaxIdentifierType, TaxProfileStatus


class TaxProfile(BaseModel):
    __tablename__ = "tax_profiles"

    business_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    jurisdiction: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, comment="Country or state the profile is filed under"
    )
    filing_frequency: Mapped[str | None] = mapped_column(String(30), nullable=True)
    fiscal_year_end: Mapped[str | None] = mapped_column(
        String(5), nullable=True, comment="MM-DD of the fiscal year end"
    )
    status: Mapped[TaxProfileStatus] = mapped_column(
        String(20), default=TaxProfileStatus.ACTIVE, nullable=False, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    business: Mapped["Business"] = relationship(back_populates="tax_profiles")
    identifiers: Mapped[list["TaxIdentifier"]] = relationship(
        back_populates="tax_profile", cascade="all, delete-orphan"
    )


class TaxIdentifier(BaseModel):
    """
    Represents one sensitive government identifier tied to a TaxProfile
    (EIN, SSN, VAT, TIN). `identifier_value` MUST be encrypted at the
    application layer before persisting (see core/security — application
    level field encryption, not covered by this scaffold) and
    `identifier_last4` is the only part safe to render in a list view.
    """
    __tablename__ = "tax_identifiers"

    tax_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tax_profiles.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    identifier_type: Mapped[TaxIdentifierType] = mapped_column(String(10), nullable=False, index=True)
    identifier_value_encrypted: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Encrypted at the application layer — never store plaintext"
    )
    identifier_last4: Mapped[str | None] = mapped_column(
        String(4), nullable=True, comment="Last 4 characters — safe for masked display"
    )
    issued_country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    issued_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    tax_profile: Mapped["TaxProfile"] = relationship(back_populates="identifiers")
