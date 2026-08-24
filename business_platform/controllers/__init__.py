"""Controllers: per-domain business logic (the only layer touching the ORM)."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession


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
    async def get_all(self, *args, **kwargs):
        self._todo("BusinessController.get_all")

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
