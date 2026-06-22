import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies.db import get_db
from src.api.dependencies.auth import CurrentUser, ScopeChecker
from src.contexts.rag.schemas import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentResponse,
    QueryRequest,
    QueryResponse,
)
from src.contexts.rag.services import RAGPlatformService
from src.shared.schemas.responses import APIResponse

router = APIRouter(prefix="/rag", tags=["rag-platform"])

recruiter_write = ScopeChecker(required_scopes=["recruiter:write"])
recruiter_read = ScopeChecker(required_scopes=["recruiter:read"])


async def get_rag_service(db: AsyncSession = Depends(get_db)) -> RAGPlatformService:
    """Dependency helper injecting active RAGPlatformService context."""
    return RAGPlatformService(db)


@router.post(
    "/documents", response_model=APIResponse[KnowledgeDocumentResponse], status_code=201
)
async def ingest_document(
    payload: KnowledgeDocumentCreate,
    current_user: CurrentUser = Depends(recruiter_write),
    service: RAGPlatformService = Depends(get_rag_service),
) -> APIResponse[KnowledgeDocumentResponse]:
    """Ingests a new knowledge source document into the platform, generating embeddings and chunks."""
    doc = await service.ingest_document(
        title=payload.title,
        source_type=payload.source_type,
        content=payload.content,
        metadata_json=payload.metadata_json,
    )
    return APIResponse(
        success=True,
        data=KnowledgeDocumentResponse.model_validate(doc),
    )


@router.post("/query", response_model=APIResponse[QueryResponse])
async def query_context(
    payload: QueryRequest,
    current_user: CurrentUser = Depends(recruiter_read),
    service: RAGPlatformService = Depends(get_rag_service),
) -> APIResponse[QueryResponse]:
    """Queries the hybrid retrieval engine for relevant chunks matching a context text query."""
    results = await service.retrieve_context(
        query=payload.query,
        source_types=payload.source_types,
        limit=payload.limit,
    )
    return APIResponse(
        success=True,
        data=QueryResponse(
            query=payload.query,
            results=results,
        ),
    )


@router.delete("/documents/{document_id}", response_model=APIResponse[dict])
async def delete_document(
    document_id: uuid.UUID,
    current_user: CurrentUser = Depends(recruiter_write),
    service: RAGPlatformService = Depends(get_rag_service),
) -> APIResponse[dict]:
    """Deletes a knowledge document and its associated chunks from vectors and database indexes."""
    await service.delete_document(document_id)
    return APIResponse(
        success=True,
        data={"message": f"KnowledgeDocument '{document_id}' successfully deleted."},
    )
