from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional, Type, TypeVar

from sqlalchemy import DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, registry

T = TypeVar("T", bound="BaseModel")


class Base(AsyncAttrs, DeclarativeBase):
    registry = registry()
    __abstract__ = True
    __type_annotation_map__ = {
        datetime: DateTime(timezone=True),
    }


class BaseMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="Unique identifier for the record (UUID)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        index=True,
        comment="Timestamp when the record was created",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False,
        index=True,
        comment="Timestamp when the record was last updated",
    )
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        index=True,
        nullable=True,
        comment="UUID of the user who created this record",
    )
    updated_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        index=True,
        nullable=True,
        comment="UUID of the user who last updated this record",
    )
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        index=True,
        nullable=False,
        comment="Flag indicating if the record has been soft-deleted",
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp when the record was soft-deleted",
    )
    deleted_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        index=True,
        nullable=True,
        comment="UUID of the user who soft-deleted this record",
    )
    version: Mapped[int] = mapped_column(
        default=1,
        nullable=False,
        comment="Version number for optimistic concurrency control",
    )


class BaseModel(BaseMixin, Base):
    __abstract__ = True

    @classmethod
    async def get_by_id(cls: Type[T], session: Any, id: uuid.UUID) -> Optional[T]:
        """Retrieve a record by primary key UUID using the async session."""
        return await session.get(cls, id)
