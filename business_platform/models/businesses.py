from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    Enum as SAEnum,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from business_platform.db.base import BaseModel
from business_platform.models.user import User
from business_platform.utils.enums import (
    BusinessStatus,
    BusinessType,
    LegalStructure,
    OwnershipType,
)


class Business(BaseModel):
    __tablename__ = "businesses"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    legal_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    display_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    business_type: Mapped[BusinessType] = mapped_column(
        SAEnum(
            BusinessType,
            name="business_type",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        default=BusinessType.BUSINESS,
        nullable=False,
        index=True,
    )

    legal_structure: Mapped[LegalStructure | None] = mapped_column(
        SAEnum(
            LegalStructure,
            name="legal_structure",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=True,
    )

    status: Mapped[BusinessStatus] = mapped_column(
        SAEnum(
            BusinessStatus,
            name="business_status",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        default=BusinessStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    registration_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    tax_identification_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    incorporation_date: Mapped[Date | None] = mapped_column(
        Date,
        nullable=True,
    )

    country_of_incorporation: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    state_of_incorporation: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(320),
        nullable=True,
        index=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    website: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    address_line_1: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    address_line_2: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    postal_code: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    industry: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    industry_code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    employee_count: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    annual_revenue: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 2),
        nullable=True,
    )

    currency: Mapped[str | None] = mapped_column(
        String(3),
        nullable=True,
    )

    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    stock_symbol: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )

    stock_exchange: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    owner_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[owner_user_id],
        lazy="selectin",
    )

    owned_businesses: Mapped[list["BusinessOwnership"]] = relationship(
        "BusinessOwnership",
        foreign_keys="BusinessOwnership.owner_business_id",
        back_populates="owner_business",
        cascade="all, delete-orphan",
    )

    ownerships: Mapped[list["BusinessOwnership"]] = relationship(
        "BusinessOwnership",
        foreign_keys="BusinessOwnership.owned_business_id",
        back_populates="owned_business",
        cascade="all, delete-orphan",
    )


class BusinessOwnership(BaseModel):
    """
    Represents ownership/control between two businesses.

    Example:

        Microsoft -> owns -> GitHub

    owner_business_id = Microsoft
    owned_business_id = GitHub
    """

    __tablename__ = "business_ownerships"

    owner_business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    owned_business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    ownership_type: Mapped[OwnershipType] = mapped_column(
        SAEnum(
            OwnershipType,
            name="ownership_type",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        default=OwnershipType.MAJORITY,
        nullable=False,
    )

    ownership_percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(7, 4),
        nullable=True,
    )

    owner_business: Mapped["Business"] = relationship(
        "Business",
        foreign_keys=[owner_business_id],
        back_populates="owned_businesses",
    )

    owned_business: Mapped["Business"] = relationship(
        "Business",
        foreign_keys=[owned_business_id],
        back_populates="ownerships",
    )
