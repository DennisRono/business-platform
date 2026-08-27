from __future__ import annotations
from typing import Any, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from business_platform.core.exceptions import AuthorizationError, DatabaseError
from business_platform.models.businesses import Business
from business_platform.schemas.businesses import BusinessListResponse, BusinessResponse


class _StubController:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _todo(self, method: str) -> None:
        raise NotImplementedError(f"{method} is not implemented yet.")


class AuthController(_StubController):
    async def logout(self, *args, **kwargs) -> None:
        self._todo("AuthController.logout")

    async def request_password_reset(self, *args, **kwargs) -> None:
        self._todo("AuthController.request_password_reset")

    async def confirm_password_reset(self, *args, **kwargs) -> None:
        self._todo("AuthController.confirm_password_reset")

    async def refresh(self, *args, **kwargs):
        self._todo("AuthController.refresh")


class BusinessController(_StubController):
    async def get_all(
        self,
        current_user: Any,
        skip: int = 0,
        limit: int = 20,
        q: Optional[str] = None,
        sort: Optional[str] = None,
        db: AsyncSession | None = None,
    ) -> BusinessListResponse:

        db = db or self.db

        try:

            if current_user.role not in {"admin", "manager"}:
                raise AuthorizationError(message="Not authorized to list businesses")

            query = select(Business)

            if q:
                search = f"%{q}%"

                query = query.where(
                    or_(
                        Business.name.ilike(search),
                        Business.legal_name.ilike(search),
                        Business.display_name.ilike(search),
                        Business.registration_number.ilike(search),
                        Business.industry.ilike(search),
                        Business.email.ilike(search),
                        Business.city.ilike(search),
                        Business.state.ilike(search),
                        Business.country.ilike(search),
                    )
                )

            if sort:
                descending = sort.startswith("-")
                field_name = sort[1:] if descending else sort

                allowed_fields = {
                    "name": Business.name,
                    "legal_name": Business.legal_name,
                    "created_at": Business.created_at,
                    "updated_at": Business.updated_at,
                    "industry": Business.industry,
                    "status": Business.status,
                    "business_type": Business.business_type,
                    "employee_count": Business.employee_count,
                    "annual_revenue": Business.annual_revenue,
                }

                sort_field = allowed_fields.get(
                    field_name,
                    Business.created_at,
                )

                query = query.order_by(sort_field.desc() if descending else sort_field.asc())

            else:
                query = query.order_by(Business.created_at.desc())

            count_query = select(func.count()).select_from(query.order_by(None).subquery())

            total = await db.scalar(count_query) or 0

            query = query.offset(skip).limit(limit)

            result = await db.execute(query)

            businesses = result.scalars().all()

            return BusinessListResponse(
                items=[BusinessResponse.model_validate(business) for business in businesses],
                total=total,
                page=(skip // limit) + 1 if limit > 0 else 1,
                size=limit,
                pages=((total + limit - 1) // limit if limit > 0 else 1),
            )

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch businesses") from exc

    async def create(self, *args, **kwargs):
        self._todo("BusinessController.create")

    async def get_by_id(self, *args, **kwargs):
        self._todo("BusinessController.get_by_id")

    async def update(self, *args, **kwargs):
        self._todo("BusinessController.update")

    async def delete(self, *args, **kwargs) -> None:
        self._todo("BusinessController.delete")

    async def get_relationships(self, *args, **kwargs):
        self._todo("BusinessController.get_relationships")

    async def create_relationship(self, *args, **kwargs):
        self._todo("BusinessController.create_relationship")


class MembershipController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("MembershipController.get_all")

    async def create(self, *args, **kwargs):
        self._todo("MembershipController.create")

    async def update(self, *args, **kwargs):
        self._todo("MembershipController.update")


class BusinessPeopleController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("BusinessPeopleController.get_all")

    async def create(self, *args, **kwargs):
        self._todo("BusinessPeopleController.create")


class PersonController(_StubController):
    async def get_by_id(self, *args, **kwargs):
        self._todo("PersonController.get_by_id")

    async def update(self, *args, **kwargs):
        self._todo("PersonController.update")

    async def get_business_relationships(self, *args, **kwargs):
        self._todo("PersonController.get_business_relationships")


class OwnershipController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("OwnershipController.get_all")

    async def create(self, *args, **kwargs):
        self._todo("OwnershipController.create")

    async def transition(self, *args, **kwargs):
        self._todo("OwnershipController.transition")


class LeadershipController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("LeadershipController.get_all")

    async def create(self, *args, **kwargs):
        self._todo("LeadershipController.create")


class EmployeeController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("EmployeeController.get_all")

    async def create(self, *args, **kwargs):
        self._todo("EmployeeController.create")

    async def get_history(self, *args, **kwargs):
        self._todo("EmployeeController.get_history")

    async def terminate(self, *args, **kwargs) -> None:
        self._todo("EmployeeController.terminate")


class CompensationController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("CompensationController.get_all")

    async def create(self, *args, **kwargs):
        self._todo("CompensationController.create")

    async def get_history(self, *args, **kwargs):
        self._todo("CompensationController.get_history")

    async def summary(self, *args, **kwargs):
        self._todo("CompensationController.summary")


class TaxController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("TaxController.get_all")

    async def create(self, *args, **kwargs):
        self._todo("TaxController.create")

    async def get_identifiers(self, *args, **kwargs):
        self._todo("TaxController.get_identifiers")


class DocumentController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("DocumentController.get_all")

    async def create(self, *args, **kwargs):
        self._todo("DocumentController.create")

    async def get_by_id(self, *args, **kwargs):
        self._todo("DocumentController.get_by_id")

    async def get_versions(self, *args, **kwargs):
        self._todo("DocumentController.get_versions")


class EventController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("EventController.get_all")

    async def create(self, *args, **kwargs):
        self._todo("EventController.create")

    async def update(self, *args, **kwargs):
        self._todo("EventController.update")


class FinancialController(_StubController):
    async def get_transactions(self, *args, **kwargs):
        self._todo("FinancialController.get_transactions")

    async def create_transaction(self, *args, **kwargs):
        self._todo("FinancialController.create_transaction")

    async def get_accounts(self, *args, **kwargs):
        self._todo("FinancialController.get_accounts")

    async def summary(self, *args, **kwargs):
        self._todo("FinancialController.summary")


class ContactController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("ContactController.get_all")

    async def create(self, *args, **kwargs):
        self._todo("ContactController.create")

    async def get_by_id(self, *args, **kwargs):
        self._todo("ContactController.get_by_id")


class DashboardController(_StubController):
    async def overview(self, *args, **kwargs):
        self._todo("DashboardController.overview")

    async def upcoming(self, *args, **kwargs):
        self._todo("DashboardController.upcoming")


class AuditLogController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("AuditLogController.get_all")
