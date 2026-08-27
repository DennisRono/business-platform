from __future__ import annotations

from business_platform.controllers.base import _StubController


class DocumentController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("DocumentController.get_all")

    async def create(self, *args, **kwargs):
        self._todo("DocumentController.create")

    async def get_by_id(self, *args, **kwargs):
        self._todo("DocumentController.get_by_id")

    async def get_versions(self, *args, **kwargs):
        self._todo("DocumentController.get_versions")
