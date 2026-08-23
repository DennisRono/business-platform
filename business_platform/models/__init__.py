"""ORM model registry.

CRITICAL: every SQLAlchemy model MUST be imported here. This module is how
Alembic's ``--autogenerate`` discovers table metadata via ``Base.metadata`` — a
model defined but not imported in this file is invisible to migrations, which
is a common and easy-to-miss source of "why is my table missing" bugs. When you
add a domain, add its model import below.
"""

from __future__ import annotations

from business_platform.db.base import Base, BaseModel
from business_platform.models.user import User

__all__ = ["Base", "BaseModel", "User"]
