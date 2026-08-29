from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers.base import _StubController
from business_platform.core.exceptions import (
    BusinessLogicError,
    ConflictError,
    DatabaseError,
    NotFoundError,
)
from business_platform.models.business import Business
from business_platform.models.document import Document, DocumentVersion
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentVersionCreate,
    DocumentVersionResponse,
)


class DocumentController(_StubController):
    async def get_all(
        self,
        business_id: UUID,
        page: int = 1,
        size: int = 20,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[DocumentResponse]:
        db = db or self.db

        try:
            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            offset = (page - 1) * size

            count_stmt = (
                select(func.count())
                .select_from(Document)
                .where(Document.business_id == business_id)
            )

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = (
                select(Document)
                .where(Document.business_id == business_id)
                .order_by(Document.created_at.desc())
                .offset(offset)
                .limit(size)
            )

            result = await db.execute(stmt)
            documents = result.scalars().all()

            items = [DocumentResponse.model_validate(document) for document in documents]

            return PaginatedResponse[DocumentResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=url_base or f"/businesses/{business_id}/documents",
            )

        except NotFoundError:
            raise

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch documents") from exc

    async def create(
        self,
        business_id: UUID,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
        uploaded_by_id: UUID | None = None,
    ) -> DocumentResponse:
        db = db or self.db

        try:
            document_create = DocumentCreate(**payload)

            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            document_data = document_create.model_dump(exclude_none=True)
            document_data["business_id"] = business_id

            if uploaded_by_id is not None:
                document_data["uploaded_by_id"] = uploaded_by_id

            new_document = Document(**document_data)

            db.add(new_document)

            await db.flush()
            await db.refresh(new_document)

            return DocumentResponse.model_validate(new_document)

        except (NotFoundError, BusinessLogicError, ConflictError):
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(
                message=(
                    "Document could not be created because "
                    "the supplied data conflicts with an existing record"
                )
            ) from exc

        except SQLAlchemyError as exc:
            await db.rollback()

            raise DatabaseError(message="Failed to create document") from exc

    async def get_by_id(
        self,
        business_id: UUID,
        document_id: UUID,
        db: AsyncSession | None = None,
    ) -> DocumentResponse:
        db = db or self.db

        try:
            stmt = select(Document).where(
                Document.id == document_id,
                Document.business_id == business_id,
            )

            result = await db.execute(stmt)
            document = result.scalar_one_or_none()

            if not document:
                raise NotFoundError(
                    message=(
                        f"Document with ID {document_id} not found "
                        f"for business {business_id}"
                    )
                )

            return DocumentResponse.model_validate(document)

        except NotFoundError:
            raise

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch document") from exc

    async def get_versions(
        self,
        business_id: UUID,
        document_id: UUID,
        page: int = 1,
        size: int = 20,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[DocumentVersionResponse]:
        db = db or self.db

        try:
            document_stmt = select(Document).where(
                Document.id == document_id,
                Document.business_id == business_id,
            )

            document_result = await db.execute(document_stmt)
            document = document_result.scalar_one_or_none()

            if not document:
                raise NotFoundError(
                    message=(
                        f"Document with ID {document_id} not found "
                        f"for business {business_id}"
                    )
                )

            offset = (page - 1) * size

            count_stmt = (
                select(func.count())
                .select_from(DocumentVersion)
                .where(DocumentVersion.document_id == document_id)
            )

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = (
                select(DocumentVersion)
                .where(DocumentVersion.document_id == document_id)
                .order_by(DocumentVersion.version_number.desc())
                .offset(offset)
                .limit(size)
            )

            result = await db.execute(stmt)
            versions = result.scalars().all()

            items = [DocumentVersionResponse.model_validate(version) for version in versions]

            return PaginatedResponse[DocumentVersionResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=url_base
                or f"/businesses/{business_id}/documents/{document_id}/versions",
            )

        except NotFoundError:
            raise

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch document versions") from exc
