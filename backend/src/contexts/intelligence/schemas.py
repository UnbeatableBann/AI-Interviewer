from datetime import datetime
import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from src.contexts.interview.schemas import InterviewSessionResponse


class SkillCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(
        ..., description="E.g., TECHNICAL, SYSTEM_DESIGN, COMMUNICATION."
    )
    description: Optional[str] = None


class SkillResponse(BaseModel):
    id: uuid.UUID
    name: str
    category: str
    description: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class CandidateProfileCreate(BaseModel):
    user_id: uuid.UUID = Field(
        ..., description="Auth user ID linked to this candidate."
    )
    resume_url: Optional[str] = Field(None, max_length=512)
    experience_years: Optional[float] = Field(None, ge=0.0)
    summary: Optional[str] = None


class CandidateProfileUpdate(BaseModel):
    resume_url: Optional[str] = Field(None, max_length=512)
    experience_years: Optional[float] = Field(None, ge=0.0)
    summary: Optional[str] = None


class CandidateProfileResponse(BaseModel):
    id: uuid.UUID
    tenant_id: str
    user_id: uuid.UUID
    resume_url: Optional[str]
    experience_years: Optional[float]
    summary: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CandidateSkillResponse(BaseModel):
    id: uuid.UUID
    skill: SkillResponse
    level: float
    confidence: float
    evaluations_count: int
    last_evaluated: datetime

    model_config = ConfigDict(from_attributes=True)


class StrengthCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: str
    context_source: Optional[str] = None


class StrengthResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    context_source: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WeaknessCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: str
    context_source: Optional[str] = None


class WeaknessResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    context_source: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProgressSnapshotResponse(BaseModel):
    id: uuid.UUID
    snapshot_date: datetime
    overall_score: float
    skills_matrix: str  # JSON payload string
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewInsightCreate(BaseModel):
    session_id: uuid.UUID
    communication_score: float = Field(..., ge=0.0, le=5.0)
    confidence_score: float = Field(..., ge=0.0, le=5.0)
    technical_rating: float = Field(..., ge=0.0, le=5.0)
    key_takeaways: str


class InterviewInsightResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    communication_score: float
    confidence_score: float
    technical_rating: float
    key_takeaways: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CandidateIntelligenceReport(BaseModel):
    """Unified candidate intelligence profile returned to recruiters."""

    profile: CandidateProfileResponse
    skills: List[CandidateSkillResponse]
    strengths: List[StrengthResponse]
    weaknesses: List[WeaknessResponse]
    insights: List[InterviewInsightResponse]
    progress_snapshots: List[ProgressSnapshotResponse]

    model_config = ConfigDict(from_attributes=True)


class TimelineEvent(BaseModel):
    event_type: str  # INTERVIEW, EVALUATION, INSIGHT, SNAPSHOT
    title: str
    timestamp: datetime
    details: Dict[str, Any]


class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    properties: Dict[str, Any]


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str
    properties: Dict[str, Any]


class KnowledgeGraph(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class CandidateMemoryResponse(BaseModel):
    timeline: List[TimelineEvent]
    knowledge_graph: KnowledgeGraph
    skill_evolution: Dict[str, List[Dict[str, Any]]]
    interviews: List[InterviewSessionResponse]
    evaluations: List[Any]
    insights: List[InterviewInsightResponse]
