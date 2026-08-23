from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


class BaseModel(Base):
    """Abstract audit-aware base. Not mapped to a table of its own."""

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ── Timestamps (server-managed) ──────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ── Actor tracking (who created / updated / deleted the row) ─────────────
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )
    updated_by_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )
    deleted_by_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )

    # ── Soft delete (delete never removes a row) ─────────────────────────────
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Optimistic concurrency ───────────────────────────────────────────────
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<{self.__class__.__name__} id={self.id}>"
