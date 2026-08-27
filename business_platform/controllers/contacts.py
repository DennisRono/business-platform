from __future__ import annotations

from business_platform.controllers.base import _StubController


class ContactController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("ContactController.get_all")

    async def create(self, *args, **kwargs):
        self._todo("ContactController.create")

    async def get_by_id(self, *args, **kwargs):
        self._todo("ContactController.get_by_id")
