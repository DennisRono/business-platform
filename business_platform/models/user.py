from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from business_platform.models.base import BaseModel
from business_platform.utils.enums import Role


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="Unique login handle"
    )
    email: Mapped[str] = mapped_column(
        String(320), unique=True, nullable=False, index=True, comment="Primary contact email"
    )
    full_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Display name shown in the dashboard"
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="bcrypt hash — never expose via a schema"
    )
    role: Mapped[Role] = mapped_column(
        String(20), default=Role.CUSTOMER, nullable=False, index=True,
        comment="Coarse role carried inside the JWT",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="Whether the account can authenticate"
    )
