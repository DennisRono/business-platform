from __future__ import annotations

from enum import Enum

class Role(str, Enum):
    """Coarse role assigned to a user, carried inside the JWT."""

    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    CUSTOMER = "customer"


class TokenType(str, Enum):
    """Distinguishes access vs. refresh tokens inside the JWT ``type`` claim."""

    ACCESS = "access"
    REFRESH = "refresh"

class BusinessType(str, Enum):
    BUSINESS = "business"
    COMPANY = "company"
    NONPROFIT = "nonprofit"
    GOVERNMENT = "government"
    COOPERATIVE = "cooperative"
    PARTNERSHIP = "partnership"
    SOLE_PROPRIETORSHIP = "sole_proprietorship"


class BusinessStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DISSOLVED = "dissolved"


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


class OwnershipType(str, Enum):
    PARENT = "parent"
    SUBSIDIARY = "subsidiary"
    MAJORITY = "majority"
    MINORITY = "minority"
    JOINT_VENTURE = "joint_venture"
    AFFILIATE = "affiliate"

