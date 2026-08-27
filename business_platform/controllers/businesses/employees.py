from __future__ import annotations

from business_platform.controllers.base import _StubController


class EmployeeController(_StubController):
    async def get_all(self, *args, **kwargs):
        self._todo("EmployeeController.get_all")

    async def create(self, *args, **kwargs):
        self._todo("EmployeeController.create")

    async def get_history(self, *args, **kwargs):
        self._todo("EmployeeController.get_history")

    async def terminate(self, *args, **kwargs) -> None:
        self._todo("EmployeeController.terminate")
