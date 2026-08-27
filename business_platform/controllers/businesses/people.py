from __future__ import annotations

from business_platform.controllers.base import _StubController


class BusinessPeopleController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("BusinessPeopleController.get_all")

    async def create(self, *args, **kwargs):
        self._todo("BusinessPeopleController.create")
