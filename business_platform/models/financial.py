from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from business_platform.models.base import BaseModel
from business_platform.utils.enums import AccountStatus, AccountType, TransactionStatus, TransactionType


class FinancialAccount(BaseModel):
    """Represents one bank/financial account belonging to a Business."""
    __tablename__ = "financial_accounts"

    business_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    account_name: Mapped[str] = mapped_column(String(150), nullable=False)
    account_type: Mapped[AccountType] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[AccountStatus] = mapped_column(
        String(20), default=AccountStatus.ACTIVE, nullable=False, index=True
    )
    institution_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    account_number_masked: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="Masked display value only, e.g. '****1234'"
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, comment="ISO 4217 currency code")
    current_balance: Mapped[float | None] = mapped_column(
        Numeric(18, 2), nullable=True, comment="Cached balance — recomputed from transactions periodically"
    )
    opened_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    closed_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    business: Mapped["Business"] = relationship(back_populates="financial_accounts")
    transactions: Mapped[list["FinancialTransaction"]] = relationship(back_populates="account")


class FinancialTransaction(BaseModel):
    """Represents one posted financial transaction against a FinancialAccount."""
    __tablename__ = "financial_transactions"

    business_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    account_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("financial_accounts.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    transaction_type: Mapped[TransactionType] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[TransactionStatus] = mapped_column(
        String(20), default=TransactionStatus.COMPLETED, nullable=False, index=True
    )
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference_number: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    counterparty_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    business: Mapped["Business"] = relationship(back_populates="financial_transactions")
    account: Mapped["FinancialAccount"] = relationship(back_populates="transactions")
