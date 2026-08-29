import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from business_platform.schemas.base import BaseSchema
from business_platform.utils.enums import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    """Shared fields used across Create and Update schemas."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[uuid.UUID] = None
    related_event_id: Optional[uuid.UUID] = None


class TaskCreate(TaskBase):
    """Schema for creating a new task. Inherits all base fields."""
    status: TaskStatus = Field(default=TaskStatus.PENDING)

    model_config = ConfigDict(extra="forbid")


class TaskUpdate(BaseModel):
    """Schema for partially updating a task. All fields are optional."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(extra="forbid")


class TaskResponse(TaskBase, BaseSchema):
    """Full response schema for a task record."""
    business_id: uuid.UUID
    status: TaskStatus
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="ignore",
    )
