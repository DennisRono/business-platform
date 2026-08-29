from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import DataError, IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers.base import _StubController
from business_platform.core.exceptions import (
    BadRequestError,
    BusinessLogicError,
    ConflictError,
    DatabaseError,
    NotFoundError,
)
from business_platform.models.business import Business
from business_platform.models.financial import FinancialAccount, FinancialTransaction
from business_platform.schemas.aggregates import FinancialSummaryResponse
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.financial import (
    FinancialAccountCreate,
    FinancialAccountResponse,
    FinancialTransactionCreate,
    FinancialTransactionResponse,
)
from business_platform.utils.enums import TransactionType


class FinancialController(_StubController):
    async def get_transactions(
        self,
        business_id: UUID,
        page: int = 1,
        size: int = 20,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[FinancialTransactionResponse]:
        db = db or self.db

        try:
            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            offset = (page - 1) * size

            count_stmt = (
                select(func.count())
                .select_from(FinancialTransaction)
                .where(FinancialTransaction.business_id == business_id)
            )

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = (
                select(FinancialTransaction)
                .where(FinancialTransaction.business_id == business_id)
                .order_by(FinancialTransaction.transaction_date.desc())
                .offset(offset)
                .limit(size)
            )

            result = await db.execute(stmt)
            transactions = result.scalars().all()

            items = [
                FinancialTransactionResponse.model_validate(transaction)
                for transaction in transactions
            ]

            return PaginatedResponse[FinancialTransactionResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=url_base or f"/businesses/{business_id}/financials/transactions",
            )

        except NotFoundError:
            raise

        except (DataError, OperationalError) as exc:
            raise BadRequestError(
                message="Invalid query parameters caused a database error."
            ) from exc

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch financial transactions") from exc

    async def create_transaction(
        self,
        business_id: UUID,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> FinancialTransactionResponse:
        db = db or self.db

        try:
            transaction_create = FinancialTransactionCreate(**payload)

            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            account_stmt = select(FinancialAccount).where(
                FinancialAccount.id == transaction_create.account_id,
                FinancialAccount.business_id == business_id,
            )

            account_result = await db.execute(account_stmt)
            account = account_result.scalar_one_or_none()

            if not account:
                raise NotFoundError(
                    message=(
                        f"Financial account with ID {transaction_create.account_id} "
                        f"not found for business {business_id}"
                    )
                )

            transaction_data = transaction_create.model_dump(exclude_none=True)
            transaction_data["business_id"] = business_id

            new_transaction = FinancialTransaction(**transaction_data)

            db.add(new_transaction)

            await db.flush()
            await db.refresh(new_transaction)

            return FinancialTransactionResponse.model_validate(new_transaction)

        except (NotFoundError, BusinessLogicError, ConflictError):
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(
                message=(
                    "Financial transaction could not be created because "
                    "the supplied data conflicts with an existing record"
                )
            ) from exc

        except (DataError, OperationalError) as exc:
            await db.rollback()
            raise BadRequestError(
                message="The request contains invalid data that could not be processed."
            ) from exc

        except SQLAlchemyError as exc:
            await db.rollback()

            raise DatabaseError(message="Failed to create financial transaction") from exc

    async def get_accounts(
        self,
        business_id: UUID,
        page: int = 1,
        size: int = 20,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[FinancialAccountResponse]:
        db = db or self.db

        try:
            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            offset = (page - 1) * size

            count_stmt = (
                select(func.count())
                .select_from(FinancialAccount)
                .where(FinancialAccount.business_id == business_id)
            )

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = (
                select(FinancialAccount)
                .where(FinancialAccount.business_id == business_id)
                .order_by(FinancialAccount.created_at.desc())
                .offset(offset)
                .limit(size)
            )

            result = await db.execute(stmt)
            accounts = result.scalars().all()

            items = [FinancialAccountResponse.model_validate(account) for account in accounts]

            return PaginatedResponse[FinancialAccountResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=url_base or f"/businesses/{business_id}/financials/accounts",
            )

        except NotFoundError:
            raise

        except (DataError, OperationalError) as exc:
            raise BadRequestError(
                message="Invalid query parameters caused a database error."
            ) from exc

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch financial accounts") from exc

    async def summary(
        self,
        business_id: UUID,
        db: AsyncSession | None = None,
    ) -> FinancialSummaryResponse:
        db = db or self.db

        try:
            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            accounts_stmt = select(FinancialAccount).where(
                FinancialAccount.business_id == business_id
            )

            accounts_result = await db.execute(accounts_stmt)
            accounts = accounts_result.scalars().all()

            currency = business.currency or (accounts[0].currency if accounts else "USD")

            total_balance = sum(
                (Decimal(str(account.current_balance)) for account in accounts if account.current_balance is not None),
                Decimal("0"),
            )

            now = datetime.now(timezone.utc)
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            transactions_stmt = select(FinancialTransaction).where(
                FinancialTransaction.business_id == business_id,
                FinancialTransaction.transaction_date >= month_start.date(),
            )

            transactions_result = await db.execute(transactions_stmt)
            transactions = transactions_result.scalars().all()

            credit_type = getattr(TransactionType, "CREDIT", None)
            debit_type = getattr(TransactionType, "DEBIT", None)

            total_credits_mtd = Decimal("0")
            total_debits_mtd = Decimal("0")

            for transaction in transactions:
                amount = Decimal(str(transaction.amount))

                if credit_type is not None and transaction.transaction_type == credit_type:
                    total_credits_mtd += amount
                elif debit_type is not None and transaction.transaction_type == debit_type:
                    total_debits_mtd += amount

            return FinancialSummaryResponse(
                business_id=business_id,
                currency=currency,
                total_balance=total_balance,
                total_credits_mtd=total_credits_mtd,
                total_debits_mtd=total_debits_mtd,
                account_count=len(accounts),
                as_of=now,
            )

        except NotFoundError:
            raise

        except (DataError, OperationalError) as exc:
            raise BadRequestError(
                message="Invalid query parameters caused a database error."
            ) from exc

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to summarize financials") from exc
