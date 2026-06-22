from datetime import datetime
import uuid
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from src.core.enums import InterviewType, InterviewStatus


class InterviewSessionCreate(BaseModel):
    candidate_id: uuid.UUID = Field(
        ..., description="Candidate profile ID to bind the session."
    )
    type: InterviewType = Field(
        ..., description="Type of interview (TECHNICAL, HR, SYSTEM_DESIGN)."
    )


class InterviewSessionResponse(BaseModel):
    id: uuid.UUID
    tenant_id: str
    candidate_id: uuid.UUID
    type: InterviewType
    status: InterviewStatus
    memory_summary: Optional[str] = None
    adaptive_state: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewQuestionResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    question_text: str
    question_type: str
    difficulty: str
    skills_assessed: Optional[List[str]] = None
    order: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewResponseCreate(BaseModel):
    response_text: str = Field(
        ..., min_length=1, description="Candidate's transcript answer content."
    )
    audio_url: Optional[str] = Field(
        None, max_length=512, description="Optional audio storage location."
    )


class InterviewResponseResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    question_id: uuid.UUID
    response_text: str
    audio_url: Optional[str] = None
    feedback: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewSessionDetailResponse(InterviewSessionResponse):
    questions: List[InterviewQuestionResponse] = []
    responses: List[InterviewResponseResponse] = []

    model_config = ConfigDict(from_attributes=True)
