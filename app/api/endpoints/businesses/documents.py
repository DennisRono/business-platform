from __future__ import annotations

import uuid
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import DocumentController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentVersionResponse,
)
from business_platform.utils.constants import AUTH_RESPONSES, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

businesses_documents_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_documents_router.get(
    "/{business_id}/documents",
    summary="List documents",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[DocumentResponse],
)
async def list_documents(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> PaginatedResponse[DocumentResponse]:
    return await DocumentController(db).get_all(
        business_id,
        page=page,
        size=size,
        url_base=f"/businesses/{business_id}/documents",
    )


@businesses_documents_router.post(
    "/{business_id}/documents",
    status_code=status.HTTP_201_CREATED,
    summary="Create a document",
    responses=AUTH_RESPONSES,
    response_model=DocumentResponse,
)
async def create_document(
    payload: DocumentCreate,
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> DocumentResponse:
    return await DocumentController(db).create(business_id, payload.model_dump(exclude_none=True))


@businesses_documents_router.get(
    "/{business_id}/documents/{document_id}",
    summary="Get a document",
    responses=AUTH_RESPONSES,
    response_model=DocumentResponse,
)
async def get_document(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    document_id: uuid.UUID,
) -> DocumentResponse:
    return await DocumentController(db).get_by_id(business_id, document_id)


@businesses_documents_router.get(
    "/{business_id}/documents/{document_id}/versions",
    summary="List document versions",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[DocumentVersionResponse],
)
async def list_document_versions(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    document_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> PaginatedResponse[DocumentVersionResponse]:
    return await DocumentController(db).get_versions(
        business_id,
        document_id,
        page=page,
        size=size,
        url_base=f"/businesses/{business_id}/documents/{document_id}/versions",
    )
