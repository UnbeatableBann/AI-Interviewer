from datetime import datetime
import uuid
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from src.contexts.intelligence.schemas import SkillResponse


class EvaluationCreatePayload(BaseModel):
    session_id: uuid.UUID = Field(
        ..., description="Active interview session to evaluate."
    )
    required_skill_levels: Optional[Dict[str, float]] = Field(
        None,
        description="Mapping of skill names to target required levels (default 4.0).",
    )


class EvaluationReportResponse(BaseModel):
    id: uuid.UUID
    tenant_id: str
    session_id: uuid.UUID
    overall_score: float
    technical_accuracy_score: float
    communication_score: float
    depth_score: float
    problem_solving_score: float
    confidence_score: float
    completeness_score: float
    summary: str
    hallucinations_detected: Optional[List[Dict[str, Any]]] = None
    faithfulness_score: float
    rubric_used: Dict[str, Any]
    extracted_evidence: List[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SkillGapReportResponse(BaseModel):
    id: uuid.UUID
    tenant_id: str
    candidate_id: uuid.UUID
    skill_id: uuid.UUID
    skill: SkillResponse
    current_level: float
    required_level: float
    gap: float
    recommendations: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
