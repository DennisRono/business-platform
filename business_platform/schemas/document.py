"""
Document / DocumentVersion Schemas
Pydantic v2 schemas for request/response validation of business
documents and their immutable uploaded versions.
"""
import uuid
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict

from business_platform.schemas.base import BaseSchema
from business_platform.utils.enums import DocumentStatus, DocumentType


class DocumentBase(BaseModel):
    """Shared fields used across Create and Update schemas."""
    document_type: DocumentType = Field(...)
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    expiry_date: Optional[date] = None


class DocumentCreate(DocumentBase):
    """Schema for creating a new document record. Inherits all base fields."""
    status: DocumentStatus = Field(default=DocumentStatus.DRAFT)


class DocumentUpdate(BaseModel):
    """Schema for partially updating a document record. All fields are optional."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[DocumentStatus] = None
    tags: Optional[List[str]] = None
    expiry_date: Optional[date] = None


class DocumentResponse(DocumentBase, BaseSchema):
    """Full response schema for a document record."""
    business_id: uuid.UUID
    status: DocumentStatus
    uploaded_by_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="ignore",
    )


class DocumentVersionCreate(BaseModel):
    """Schema for uploading a new version of an existing document."""
    file_name: str = Field(..., max_length=255)
    storage_key: str = Field(..., max_length=1024)
    mime_type: Optional[str] = Field(None, max_length=150)
    file_size_bytes: Optional[int] = Field(None, ge=0)
    checksum: Optional[str] = Field(None, max_length=128)
    change_notes: Optional[str] = None


class DocumentVersionResponse(BaseModel):
    """Represents one immutable uploaded file for a Document."""
    id: uuid.UUID
    document_id: uuid.UUID
    version_number: int
    file_name: str
    mime_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    checksum: Optional[str] = None
    change_notes: Optional[str] = None
    uploaded_by_id: Optional[uuid.UUID] = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="ignore")
