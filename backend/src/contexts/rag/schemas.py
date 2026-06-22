import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class KnowledgeDocumentCreate(BaseModel):
    """Payload to ingest a new knowledge document."""

    title: str = Field(..., max_length=255, description="Title of the source document")
    source_type: str = Field(
        ...,
        description="Source type (e.g. JOB_DESCRIPTION, COMPANY_RUBRIC, EXPECTED_ANSWER, INTERVIEW_PLAYBOOK, CANDIDATE_HISTORY)",
    )
    content: str = Field(
        ..., min_length=10, description="Raw text content of the document"
    )
    metadata_json: Optional[Dict[str, Any]] = Field(
        None, description="Optional arbitrary metadata context properties"
    )

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v: str) -> str:
        allowed = {
            "JOB_DESCRIPTION",
            "COMPANY_RUBRIC",
            "EXPECTED_ANSWER",
            "INTERVIEW_PLAYBOOK",
            "CANDIDATE_HISTORY",
        }
        upper_v = v.upper().strip()
        if upper_v not in allowed:
            raise ValueError(
                f"Invalid source_type. Must be one of: {', '.join(allowed)}"
            )
        return upper_v


class KnowledgeDocumentResponse(BaseModel):
    """Serialized document summary detail response."""

    id: uuid.UUID
    tenant_id: str
    title: str
    source_type: str
    content: str
    metadata_json: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QueryRequest(BaseModel):
    """Parameters for executing hybrid-retrieval query searches."""

    query: str = Field(
        ..., min_length=1, description="Lexical and semantic query string"
    )
    source_types: Optional[List[str]] = Field(
        None, description="Filter search scope to specific source types"
    )
    limit: int = Field(
        5, ge=1, le=50, description="Maximum search result items to return"
    )


class Citation(BaseModel):
    """Citation reference back to the original source document chunk."""

    document_id: uuid.UUID
    title: str
    source_type: str
    chunk_index: int
    content: str


class RetrievalResult(BaseModel):
    """Unified hybrid vector search result item."""

    chunk_id: uuid.UUID
    score: float
    content: str
    citation: Citation


class QueryResponse(BaseModel):
    """Full retrieved context list returned by the RAG engine."""

    query: str
    results: List[RetrievalResult]
