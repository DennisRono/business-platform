from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from business_platform.models.base import BaseModel
from business_platform.utils.enums import RelationshipStatus, RelationshipType


class BusinessRelationship(BaseModel):
    """
    Represents a directed relationship from one business to another,
    e.g. `business` owns/franchises/supplies `related_business`.
    """
    __tablename__ = "business_relationships"

    business_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    related_business_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    relationship_type: Mapped[RelationshipType] = mapped_column(
        String(30), nullable=False, index=True
    )
    status: Mapped[RelationshipStatus] = mapped_column(
        String(20), default=RelationshipStatus.ACTIVE, nullable=False, index=True
    )
    ownership_percentage: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    business: Mapped["Business"] = relationship(
        foreign_keys=[business_id], back_populates=None
    )
    related_business: Mapped["Business"] = relationship(
        foreign_keys=[related_business_id], back_populates=None
    )
