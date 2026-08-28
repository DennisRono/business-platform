from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from business_platform.models.base import BaseModel
from business_platform.utils.enums import MembershipRole, MembershipStatus


class Membership(BaseModel):
    """
    Represents a platform User's access to a Business dashboard,
    including their role and invitation lifecycle.
    """
    __tablename__ = "memberships"
    __table_args__ = ()

    business_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    role: Mapped[MembershipRole] = mapped_column(
        String(20), default=MembershipRole.STAFF, nullable=False, index=True
    )
    status: Mapped[MembershipStatus] = mapped_column(
        String(20), default=MembershipStatus.INVITED, nullable=False, index=True
    )
    invited_by_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    invited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    business: Mapped["Business"] = relationship(
        foreign_keys=[business_id], back_populates="memberships"
    )
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
