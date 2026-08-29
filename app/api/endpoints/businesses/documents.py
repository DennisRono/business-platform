from __future__ import annotations

import uuid
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import DocumentController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser
from business_platform.schemas.document import DocumentCreate, DocumentVersionCreate

businesses_documents_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_documents_router.get("/{business_id}/documents", summary="List documents")
async def list_documents(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> Any:
    return await DocumentController(db).get_all(business_id)


@businesses_documents_router.post(
    "/{business_id}/documents",
    status_code=status.HTTP_201_CREATED,
    summary="Create a document",
)
async def create_document(
    payload: DocumentCreate,
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> Any:
    return await DocumentController(db).create(business_id, payload.model_dump(exclude_none=True))


@businesses_documents_router.get("/{business_id}/documents/{document_id}", summary="Get a document")
async def get_document(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    document_id: uuid.UUID,
) -> Any:
    return await DocumentController(db).get_by_id(business_id, document_id)


@businesses_documents_router.get(
    "/{business_id}/documents/{document_id}/versions",
    summary="List document versions",
)
async def list_document_versions(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    document_id: uuid.UUID,
) -> Any:
    return await DocumentController(db).get_versions(business_id, document_id)