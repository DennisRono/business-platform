from __future__ import annotations

import uuid
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import ContactController
from business_platform.db.database import get_db
from business_platform.dependencies.auth import GetCurrentUser
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.contact import ContactCreate, ContactResponse
from business_platform.utils.constants import AUTH_RESPONSES
from business_platform.utils.pagination import PaginationQuery

contacts_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@contacts_router.get(
    "/",
    summary="List contacts",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[ContactResponse],
)
async def list_contacts(
    db: DbSession,
    _: GetCurrentUser,
    pagination: PaginationQuery,
) -> PaginatedResponse[ContactResponse]:
    return await ContactController(db).get_all(
        page=pagination.page, size=pagination.size, url_base="/contacts"
    )


@contacts_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a contact",
    responses=AUTH_RESPONSES,
    response_model=ContactResponse,
)
async def create_contact(
    payload: ContactCreate, db: DbSession, _: GetCurrentUser
) -> ContactResponse:
    return await ContactController(db).create(payload.model_dump(exclude_none=True))


@contacts_router.get(
    "/{contact_id}",
    summary="Get a contact by id",
    responses=AUTH_RESPONSES,
    response_model=ContactResponse,
)
async def get_contact(
    db: DbSession,
    _: GetCurrentUser,
    contact_id: uuid.UUID,
) -> ContactResponse:
    return await ContactController(db).get_by_id(contact_id)
