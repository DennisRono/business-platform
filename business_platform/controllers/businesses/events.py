from __future__ import annotations

from business_platform.controllers.base import _StubController


class EventController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("EventController.get_all")

    async def create(self, *args, **kwargs):
        self._todo("EventController.create")

    async def update(self, *args, **kwargs):
        self._todo("EventController.update")
