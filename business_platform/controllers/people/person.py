from __future__ import annotations

from business_platform.controllers.base import _StubController


class PersonController(_StubController):
    async def get_by_id(self, *args, **kwargs):
        self._todo("PersonController.get_by_id")

    async def update(self, *args, **kwargs):
        self._todo("PersonController.update")

    async def get_business_relationships(self, *args, **kwargs):
        self._todo("PersonController.get_business_relationships")
