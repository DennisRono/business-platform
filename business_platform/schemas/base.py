from __future__ import annotations

from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field, ConfigDict
import uuid
from datetime import datetime

T = TypeVar("T")


class PaginationLinks(BaseModel):
    self: str
    next: Optional[str] = None
    prev: Optional[str] = None
    first: str
    last: str


class PaginationMeta(BaseModel):
    total: int
    page: int
    size: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    size: int
    items: List[T]
    next_page: Optional[int] = None
    prev_page: Optional[int] = None
    links: PaginationLinks
    meta: PaginationMeta

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        size: int,
        url_base: str,
    ) -> "PaginatedResponse[T]":
        total_pages = (total + size - 1) // size
        next_page = page + 1 if page < total_pages else None
        prev_page = page - 1 if page > 1 else None

        links = PaginationLinks(
            self=f"{url_base}?page={page}&size={size}",
            next=f"{url_base}?page={next_page}&size={size}" if next_page else None,
            prev=f"{url_base}?page={prev_page}&size={size}" if prev_page else None,
            first=f"{url_base}?page=1&size={size}",
            last=f"{url_base}?page={total_pages}&size={size}",
        )

        return cls(
            total=total,
            page=page,
            size=size,
            items=items,
            next_page=next_page,
            prev_page=prev_page,
            links=links,
            meta=PaginationMeta(
                total=total,
                page=page,
                size=size,
                total_pages=total_pages,
            ),
        )


class BaseSchema(BaseModel):
    id: uuid.UUID = Field(..., description="Unique identifier for the record (UUID)")
    created_at: datetime = Field(..., description="Timestamp when the record was created")
    updated_at: datetime = Field(..., description="Timestamp when the record was last updated")
    created_by_id: Optional[uuid.UUID] = Field(None, description="UUID of the user who created this record")
    updated_by_id: Optional[uuid.UUID] = Field(None, description="UUID of the user who last updated this record")
    is_deleted: bool = Field(False, description="Flag indicating if the record has been soft-deleted")
    deleted_at: Optional[datetime] = Field(None, description="Timestamp when the record was soft-deleted")
    deleted_by_id: Optional[uuid.UUID] = Field(None, description="UUID of the user who soft-deleted this record")
    version: int = Field(1, description="Version number for optimistic concurrency control")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="ignore",
    )
