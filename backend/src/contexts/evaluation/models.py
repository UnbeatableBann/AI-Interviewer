from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy import DateTime, Float, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base
from src.contexts.interview.models import InterviewSession
from src.contexts.intelligence.models import CandidateProfile, Skill


class EvaluationReport(Base):
    """Enterprise evaluation report assessing candidate across 6 dimensions."""

    __tablename__ = "evaluation_reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 6 Core Dimensions Scores (0.0 to 5.0)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    technical_accuracy_score: Mapped[float] = mapped_column(Float, nullable=False)
    communication_score: Mapped[float] = mapped_column(Float, nullable=False)
    depth_score: Mapped[float] = mapped_column(Float, nullable=False)
    problem_solving_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    completeness_score: Mapped[float] = mapped_column(Float, nullable=False)

    summary: Mapped[str] = mapped_column(Text, nullable=False)

    # Hallucination & Faithfulness Validation
    hallucinations_detected: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSON, nullable=True
    )
    faithfulness_score: Mapped[float] = mapped_column(
        Float, default=1.0, nullable=False
    )  # 0.0 to 1.0

    # Rubrics and Evidences
    rubric_used: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    extracted_evidence: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    session: Mapped["InterviewSession"] = relationship()


class SkillGapReport(Base):
    """Identifies delta between candidate level and target proficiency level."""

    __tablename__ = "skill_gap_reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True
    )

    current_level: Mapped[float] = mapped_column(Float, nullable=False)
    required_level: Mapped[float] = mapped_column(Float, default=4.0, nullable=False)
    gap: Mapped[float] = mapped_column(Float, nullable=False)  # required - current
    recommendations: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    candidate: Mapped["CandidateProfile"] = relationship()
    skill: Mapped["Skill"] = relationship()
