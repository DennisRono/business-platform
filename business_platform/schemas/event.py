"""
Event Schemas
Pydantic v2 schemas for request/response validation of dated
business events (filing deadlines, board meetings, renewals).
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, model_validator

from business_platform.schemas.base import BaseSchema
from business_platform.utils.enums import EventStatus, EventType


class EventBase(BaseModel):
    """Shared fields used across Create and Update schemas."""
    event_type: EventType = Field(...)
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: datetime = Field(...)
    end_date: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=255)
    is_recurring: bool = Field(default=False)
    recurrence_rule: Optional[str] = Field(None, max_length=255)
    reminder_days_before: Optional[int] = Field(None, ge=0)
    related_document_id: Optional[uuid.UUID] = None

    @model_validator(mode="after")
    def check_date_order(self) -> "EventBase":
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        return self


class EventCreate(EventBase):
    """Schema for creating a new event. Inherits all base fields."""
    status: EventStatus = Field(default=EventStatus.SCHEDULED)


class EventUpdate(BaseModel):
    """Schema for partially updating an event. All fields are optional."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[EventStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=255)
    reminder_days_before: Optional[int] = Field(None, ge=0)


class EventResponse(EventBase, BaseSchema):
    """Full response schema for an event record."""
    business_id: uuid.UUID
    status: EventStatus

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="ignore",
    )
