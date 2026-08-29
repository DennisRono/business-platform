import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from business_platform.schemas.base import BaseSchema
from business_platform.utils.enums import AccountStatus, AccountType, TransactionStatus, TransactionType


class FinancialAccountBase(BaseModel):
    """Shared fields used across Create and Update schemas."""
    account_name: str = Field(..., min_length=1, max_length=150)
    account_type: AccountType = Field(...)
    institution_name: Optional[str] = Field(None, max_length=150)
    account_number_masked: Optional[str] = Field(None, max_length=20)
    currency: str = Field(..., min_length=3, max_length=3)
    opened_date: Optional[date] = None


class FinancialAccountCreate(FinancialAccountBase):
    """Schema for creating a new financial account. Inherits all base fields."""
    status: AccountStatus = Field(default=AccountStatus.ACTIVE)


class FinancialAccountUpdate(BaseModel):
    """Schema for partially updating a financial account. All fields are optional."""
    account_name: Optional[str] = Field(None, min_length=1, max_length=150)
    status: Optional[AccountStatus] = None
    closed_date: Optional[date] = None


class FinancialAccountResponse(FinancialAccountBase, BaseSchema):
    """Full response schema for a financial account record."""
    business_id: uuid.UUID
    status: AccountStatus
    current_balance: Optional[Decimal] = None
    closed_date: Optional[date] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="ignore",
    )


class FinancialTransactionBase(BaseModel):
    """Shared fields used across Create and Update schemas."""
    account_id: uuid.UUID = Field(..., description="Account this transaction posts against")
    transaction_type: TransactionType = Field(...)
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    reference_number: Optional[str] = Field(None, max_length=100)
    counterparty_name: Optional[str] = Field(None, max_length=255)
    transaction_date: date = Field(...)


class FinancialTransactionCreate(FinancialTransactionBase):
    """Schema for creating a new financial transaction. Inherits all base fields."""
    status: TransactionStatus = Field(default=TransactionStatus.COMPLETED)


class FinancialTransactionUpdate(BaseModel):
    """Schema for partially updating a financial transaction. All fields are optional."""
    status: Optional[TransactionStatus] = None
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class FinancialTransactionResponse(FinancialTransactionBase, BaseSchema):
    """Full response schema for a financial transaction record."""
    business_id: uuid.UUID
    status: TransactionStatus

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="ignore",
    )
