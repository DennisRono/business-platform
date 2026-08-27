from __future__ import annotations

from business_platform.controllers.base import _StubController


class AuditLogController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("AuditLogController.get_all")
