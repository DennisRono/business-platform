from __future__ import annotations

from fastapi import APIRouter

from .confirm import router as confirm_router
from .request import router as request_router

router = APIRouter(prefix="/password-reset", tags=["auth"])
router.include_router(request_router)
router.include_router(confirm_router)
