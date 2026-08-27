from __future__ import annotations

from business_platform.controllers.base import _StubController


class OwnershipController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("OwnershipController.get_all")

    async def create(self, *args, **kwargs):
        self._todo("OwnershipController.create")

    async def transition(self, *args, **kwargs):
        self._todo("OwnershipController.transition")
