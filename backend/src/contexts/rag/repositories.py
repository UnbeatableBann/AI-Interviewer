import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from src.contexts.tenant.repositories import TenantIsolatedRepository
from src.contexts.rag.models import KnowledgeDocument, KnowledgeChunk


class KnowledgeDocumentRepository(TenantIsolatedRepository[KnowledgeDocument]):
    """Tenant-isolated repository for KnowledgeDocument."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, KnowledgeDocument)

    async def get_document_with_chunks(
        self, document_id: uuid.UUID
    ) -> Optional[KnowledgeDocument]:
        """Retrieves a document with its nested child chunks, isolated to the active tenant."""
        stmt = (
            select(KnowledgeDocument)
            .where(KnowledgeDocument.id == document_id)
            .options(joinedload(KnowledgeDocument.chunks))
        )
        stmt = self._apply_tenant_filter(stmt)
        res = await self.db.execute(stmt)
        return res.scalars().first()


class KnowledgeChunkRepository(TenantIsolatedRepository[KnowledgeChunk]):
    """Tenant-isolated repository for KnowledgeChunk."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, KnowledgeChunk)

    async def get_tenant_chunks_with_documents(
        self, source_types: Optional[List[str]] = None
    ) -> List[KnowledgeChunk]:
        """Loads all chunks for the active tenant, pre-loading parent documents to support hybrid search and citations."""
        stmt = (
            select(KnowledgeChunk)
            .join(KnowledgeChunk.document)
            .options(joinedload(KnowledgeChunk.document))
        )
        if source_types:
            stmt = stmt.where(KnowledgeDocument.source_type.in_(source_types))

        stmt = self._apply_tenant_filter(stmt)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_by_document(self, document_id: uuid.UUID) -> List[KnowledgeChunk]:
        """Loads all chunks belonging to a target document, sorted sequentially by chunk index."""
        stmt = (
            select(KnowledgeChunk)
            .where(KnowledgeChunk.document_id == document_id)
            .order_by(KnowledgeChunk.chunk_index.asc())
        )
        stmt = self._apply_tenant_filter(stmt)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
