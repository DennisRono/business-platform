from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession


class _StubController:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _todo(self, method: str) -> None:
        raise NotImplementedError(f"{method} is not implemented yet.")
