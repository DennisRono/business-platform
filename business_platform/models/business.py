from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from business_platform.models.base import BaseModel
from business_platform.utils.enums import BusinessStatus, BusinessType, LegalStructure


class Business(BaseModel):
    """
    Represents a business entity (company, nonprofit, government body,
    cooperative, partnership, or sole proprietorship). Mirrors the
    BusinessCreate schema field-for-field.
    """
    __tablename__ = "businesses"

    # Identity
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="Legal or primary business name"
    )
    legal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    business_type: Mapped[BusinessType] = mapped_column(
        String(30), default=BusinessType.BUSINESS, nullable=False, index=True
    )
    legal_structure: Mapped[LegalStructure | None] = mapped_column(String(30), nullable=True)
    status: Mapped[BusinessStatus] = mapped_column(
        String(20), default=BusinessStatus.ACTIVE, nullable=False, index=True
    )

    # Registration / incorporation
    registration_number: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    tax_identification_number: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    incorporation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    country_of_incorporation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state_of_incorporation: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Contact
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    website: Mapped[str | None] = mapped_column(String(2083), nullable=True)

    # Address
    address_line_1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(30), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # Classification / size
    industry: Mapped[str | None] = mapped_column(String(150), nullable=True, index=True)
    industry_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    employee_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    annual_revenue: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True, comment="ISO 4217 currency code")

    # Public markets
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    stock_symbol: Mapped[str | None] = mapped_column(String(20), nullable=True)
    stock_exchange: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationships
    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    owners: Mapped[list["OwnershipRecord"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    leaders: Mapped[list["Leader"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    employees: Mapped[list["Employee"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    compensation_records: Mapped[list["CompensationRecord"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    tax_profiles: Mapped[list["TaxProfile"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    events: Mapped[list["Event"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    financial_accounts: Mapped[list["FinancialAccount"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    financial_transactions: Mapped[list["FinancialTransaction"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    contacts: Mapped[list["Contact"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
