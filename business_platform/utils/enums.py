from enum import Enum


class Role(str, Enum):
    """Coarse role assigned to a platform user, carried inside the JWT."""
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    CUSTOMER = "customer"


class BusinessType(str, Enum):
    BUSINESS = "business"
    COMPANY = "company"
    NONPROFIT = "nonprofit"
    GOVERNMENT = "government"
    COOPERATIVE = "cooperative"
    PARTNERSHIP = "partnership"
    SOLE_PROPRIETORSHIP = "sole_proprietorship"


class LegalStructure(str, Enum):
    SOLE_PROPRIETORSHIP = "sole_proprietorship"
    PARTNERSHIP = "partnership"
    LLC = "llc"
    C_CORPORATION = "c_corporation"
    S_CORPORATION = "s_corporation"
    NONPROFIT = "nonprofit"
    COOPERATIVE = "cooperative"
    GOVERNMENT_ENTITY = "government_entity"
    OTHER = "other"


class BusinessStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DISSOLVED = "dissolved"


class RelationshipType(str, Enum):
    """Nature of a relationship between two businesses."""
    PARENT_SUBSIDIARY = "parent_subsidiary"
    JOINT_VENTURE = "joint_venture"
    FRANCHISE = "franchise"
    SUPPLIER = "supplier"
    PARTNER = "partner"
    AFFILIATE = "affiliate"
    OTHER = "other"


class RelationshipStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"


class MembershipRole(str, Enum):
    """Role a platform User holds inside a specific Business."""
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    VIEWER = "viewer"


class MembershipStatus(str, Enum):
    ACTIVE = "active"
    INVITED = "invited"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


class OwnershipType(str, Enum):
    EQUITY = "equity"
    SHARES = "shares"
    MEMBERSHIP_INTEREST = "membership_interest"
    PARTNERSHIP_INTEREST = "partnership_interest"


class OwnershipStatus(str, Enum):
    """
    State machine for an OwnershipRecord. Transitions are made via
    PATCH /business/{id}/owners/{id} and logged in OwnershipTransition
    for a full audit trail.
    """
    PENDING = "pending"
    ACTIVE = "active"
    TRANSFERRED = "transferred"
    DIVESTED = "divested"


class LeaderTitle(str, Enum):
    CEO = "ceo"
    CFO = "cfo"
    COO = "coo"
    PRESIDENT = "president"
    DIRECTOR = "director"
    CHAIRMAN = "chairman"
    SECRETARY = "secretary"
    TREASURER = "treasurer"
    GENERAL_MANAGER = "general_manager"
    OTHER = "other"


class LeaderStatus(str, Enum):
    ACTIVE = "active"
    RESIGNED = "resigned"
    REMOVED = "removed"


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERN = "intern"
    SEASONAL = "seasonal"


class EmploymentStatus(str, Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"
    RESIGNED = "resigned"


class EmployeeHistoryEventType(str, Enum):
    HIRE = "hire"
    PROMOTION = "promotion"
    TRANSFER = "transfer"
    STATUS_CHANGE = "status_change"
    TERMINATION = "termination"
    REHIRE = "rehire"


class CompensationType(str, Enum):
    SALARY = "salary"
    HOURLY = "hourly"
    COMMISSION = "commission"
    BONUS = "bonus"
    EQUITY = "equity"
    OTHER = "other"


class CompensationFrequency(str, Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    ANNUALLY = "annually"
    ONE_TIME = "one_time"


class TaxProfileStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNDER_REVIEW = "under_review"


class TaxIdentifierType(str, Enum):
    """
    NOTE: values stored against TaxIdentifier.identifier_value are
    sensitive (PII / government identifiers). See models/tax.py for
    handling notes.
    """
    EIN = "ein"
    SSN = "ssn"
    VAT = "vat"
    TIN = "tin"
    OTHER = "other"


class DocumentType(str, Enum):
    CONTRACT = "contract"
    INCORPORATION_CERTIFICATE = "incorporation_certificate"
    TAX_FILING = "tax_filing"
    LICENSE = "license"
    PERMIT = "permit"
    FINANCIAL_STATEMENT = "financial_statement"
    OTHER = "other"


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    EXPIRED = "expired"


class EventType(str, Enum):
    FILING_DEADLINE = "filing_deadline"
    BOARD_MEETING = "board_meeting"
    LICENSE_RENEWAL = "license_renewal"
    COMPLIANCE_REVIEW = "compliance_review"
    OTHER = "other"


class EventStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_LINE = "credit_line"
    ESCROW = "escrow"
    OTHER = "other"


class AccountStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    FROZEN = "frozen"


class TransactionType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    TRANSFER = "transfer"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"


class ContactType(str, Enum):
    PRIMARY = "primary"
    BILLING = "billing"
    LEGAL = "legal"
    EMERGENCY = "emergency"
    OTHER = "other"
