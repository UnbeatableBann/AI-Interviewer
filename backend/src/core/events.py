from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """Base event structure for all platform events to ensure strict metadata isolation."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tenant_id: str


class InterviewStarted(BaseEvent):
    """Triggered when a candidate starts an interview session."""

    interview_id: str
    candidate_id: str
    template_id: Optional[str] = None
    interviewer_id: str

    def __init__(self, **data: Any) -> None:
        data["event_type"] = "InterviewStarted"
        super().__init__(**data)


class QuestionGenerated(BaseEvent):
    """Triggered when the adaptive interview engine constructs a new question."""

    interview_id: str
    question_id: str
    question_text: str
    category: str  # technical, system_design, hr, etc.

    def __init__(self, **data: Any) -> None:
        data["event_type"] = "QuestionGenerated"
        super().__init__(**data)


class AnswerReceived(BaseEvent):
    """Triggered when a candidate submits an answer to an active question."""

    interview_id: str
    question_id: str
    answer_text: str
    confidence_level: Optional[float] = None

    def __init__(self, **data: Any) -> None:
        data["event_type"] = "AnswerReceived"
        super().__init__(**data)


class EvaluationCompleted(BaseEvent):
    """Triggered when the evaluation engine finishes analyzing an interview."""

    evaluation_id: str
    interview_id: str
    candidate_id: str
    scores: Dict[str, float]
    overall_score: float
    hallucinations_detected: int
    faithfulness_ratio: float

    def __init__(self, **data: Any) -> None:
        data["event_type"] = "EvaluationCompleted"
        super().__init__(**data)


class CandidateUpdated(BaseEvent):
    """Triggered when a candidate profile or skills graph is updated."""

    candidate_id: str
    profile_changes: Dict[str, Any]

    def __init__(self, **data: Any) -> None:
        data["event_type"] = "CandidateUpdated"
        super().__init__(**data)


class AnalyticsUpdated(BaseEvent):
    """Triggered when recruiter analytics or telemetry metrics are updated."""

    metric_name: str
    value: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data: Any) -> None:
        data["event_type"] = "AnalyticsUpdated"
        super().__init__(**data)


# Map of event_type string to Class for deserialization helper
EVENT_MAP = {
    "InterviewStarted": InterviewStarted,
    "QuestionGenerated": QuestionGenerated,
    "AnswerReceived": AnswerReceived,
    "EvaluationCompleted": EvaluationCompleted,
    "CandidateUpdated": CandidateUpdated,
    "AnalyticsUpdated": AnalyticsUpdated,
}


def deserialize_event(event_type: str, data: Dict[str, Any]) -> BaseEvent:
    """Helper method to deserialize generic dict data into specific event model."""
    event_cls = EVENT_MAP.get(event_type)
    if not event_cls:
        raise ValueError(f"Unknown event type: {event_type}")
    return event_cls(**data)
