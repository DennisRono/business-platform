from __future__ import annotations

from business_platform.controllers.base import _StubController


class DashboardController(_StubController):
    async def overview(self, *args, **kwargs):
        self._todo("DashboardController.overview")

    async def upcoming(self, *args, **kwargs):
        self._todo("DashboardController.upcoming")
