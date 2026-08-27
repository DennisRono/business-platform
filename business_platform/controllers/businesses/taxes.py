from __future__ import annotations

from business_platform.controllers.base import _StubController


class TaxController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("TaxController.get_all")

    async def create(self, *args, **kwargs):
        self._todo("TaxController.create")

    async def get_identifiers(self, *args, **kwargs):
        self._todo("TaxController.get_identifiers")
