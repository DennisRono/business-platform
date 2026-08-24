from __future__ import annotations

import uuid
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import DocumentController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser

router = APIRouter(tags=["businesses"])

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@router.get("/{business_id}/documents", summary="List documents")
async def list_documents(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> Any:
    return await DocumentController(db).get_all(business_id)


@router.post(
    "/{business_id}/documents",
    status_code=status.HTTP_201_CREATED,
    summary="Create a document",
)
async def create_document(
    payload: dict[str, Any],
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> Any:
    return await DocumentController(db).create(business_id, payload)


@router.get("/{business_id}/documents/{document_id}", summary="Get a document")
async def get_document(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    document_id: uuid.UUID,
) -> Any:
    return await DocumentController(db).get_by_id(business_id, document_id)


@router.get(
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