"""
Aggregate Response Schemas
Response shapes for GET endpoints that are computed from more than one
table and therefore have no single backing ORM model:
  - GET /dashboard/overview
  - GET /dashboard/upcoming
  - GET /business/{id}/compensation/summary
  - GET /business/{id}/financials/summary
  - GET /people/{id}/business-relationships
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from business_platform.utils.enums import (
    CompensationType,
    EmploymentStatus,
    LeaderTitle,
    OwnershipType,
)


class DashboardOverviewResponse(BaseModel):
    """Top-level counts shown on the dashboard landing page."""
    total_businesses: int = 0
    active_businesses: int = 0
    total_people: int = 0
    total_employees: int = 0
    open_tasks: int = 0
    upcoming_events_count: int = 0
    pending_ownership_transitions: int = 0

    model_config = ConfigDict(extra="ignore")


class UpcomingItemResponse(BaseModel):
    """One row in the dashboard's combined events/tasks upcoming feed."""
    item_type: str = Field(..., description="'event' or 'task'")
    id: uuid.UUID
    business_id: uuid.UUID
    title: str
    due_at: datetime

    model_config = ConfigDict(extra="ignore")


class CompensationSummaryResponse(BaseModel):
    """Aggregated compensation figures for a Business, computed on read."""
    business_id: uuid.UUID
    currency: str
    total_current_annualized: Decimal
    by_type: dict[CompensationType, Decimal] = Field(default_factory=dict)
    headcount_compensated: int

    model_config = ConfigDict(extra="ignore")


class FinancialSummaryResponse(BaseModel):
    """Aggregated financial position for a Business, computed on read."""
    business_id: uuid.UUID
    currency: str
    total_balance: Decimal
    total_credits_mtd: Decimal
    total_debits_mtd: Decimal
    account_count: int
    as_of: datetime

    model_config = ConfigDict(extra="ignore")


class PersonBusinessRelationshipResponse(BaseModel):
    """
    One row summarizing a Person's involvement with a single Business —
    composed from OwnershipRecord, Leader, and Employee, whichever
    apply. Read-only; there is no backing table for this shape.
    """
    business_id: uuid.UUID
    business_name: str
    is_owner: bool = False
    ownership_type: Optional[OwnershipType] = None
    ownership_percentage: Optional[Decimal] = None
    is_leader: bool = False
    leader_title: Optional[LeaderTitle] = None
    is_employee: bool = False
    employment_status: Optional[EmploymentStatus] = None
    job_title: Optional[str] = None

    model_config = ConfigDict(extra="ignore")
