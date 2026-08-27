from __future__ import annotations

from business_platform.controllers.base import _StubController


class FinancialController(_StubController):
    async def get_transactions(self, *args, **kwargs):
        self._todo("FinancialController.get_transactions")

    async def create_transaction(self, *args, **kwargs):
        self._todo("FinancialController.create_transaction")

    async def get_accounts(self, *args, **kwargs):
        self._todo("FinancialController.get_accounts")

    async def summary(self, *args, **kwargs):
        self._todo("FinancialController.summary")
