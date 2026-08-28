from __future__ import annotations

import uuid
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import TaxController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import (
    BusinessAccessUser,
    SensitiveDataUser,
)

businesses_taxes_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_taxes_router.get("/{business_id}/taxes", summary="List tax profiles")
async def list_taxes(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> Any:
    return await TaxController(db).get_all(business_id)


@businesses_taxes_router.post(
    "/{business_id}/taxes",
    status_code=status.HTTP_201_CREATED,
    summary="Create a tax profile",
)
async def create_tax_profile(
    payload: dict[str, Any],
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> Any:
    return await TaxController(db).create(business_id, payload)


@businesses_taxes_router.get(
    "/{business_id}/taxes/{tax_profile_id}/identifiers",
    summary="List sensitive tax identifiers",
)
async def list_tax_identifiers(
    db: DbSession,
    _: SensitiveDataUser,
    business_id: uuid.UUID,
    tax_profile_id: uuid.UUID,
) -> Any:
    # TODO: make this request auditable through the audit dependency pipeline.
    return await TaxController(db).get_identifiers(business_id, tax_profile_id)