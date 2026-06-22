from datetime import datetime, timezone
import uuid
from typing import List, Optional, Any
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base
from src.core.enums import InterviewType, InterviewStatus
from src.contexts.intelligence.models import CandidateProfile


class InterviewSession(Base):
    """Interview Session tracking the state machine, type, and memory."""

    __tablename__ = "interview_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type: Mapped[InterviewType] = mapped_column(String(50), nullable=False)
    status: Mapped[InterviewStatus] = mapped_column(
        String(50), default=InterviewStatus.CREATED, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Memory and Adaptive features
    memory_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    adaptive_state: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )  # Store current difficulty, focus skills, history summary

    # Relationships
    candidate: Mapped["CandidateProfile"] = relationship()
    questions: Mapped[List["InterviewQuestion"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="InterviewQuestion.order",
    )
    responses: Mapped[List["InterviewResponse"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class InterviewQuestion(Base):
    """Adaptive questions generated during the session."""

    __tablename__ = "interview_questions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(
        String(50), default="PRIMARY", nullable=False
    )  # PRIMARY, FOLLOW_UP
    expected_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(
        String(20), default="MEDIUM", nullable=False
    )  # EASY, MEDIUM, HARD
    skills_assessed: Mapped[Optional[List[str]]] = mapped_column(
        JSON, nullable=True
    )  # List of skills: ["Python", "Concurrency"]
    order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    session: Mapped["InterviewSession"] = relationship(back_populates="questions")
    responses: Mapped[List["InterviewResponse"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )


class InterviewResponse(Base):
    """Candidate's responses and the evaluation/feedback generated per question."""

    __tablename__ = "interview_responses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("interview_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    audio_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    feedback: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )  # score, critique, alignment

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    session: Mapped["InterviewSession"] = relationship(back_populates="responses")
    question: Mapped["InterviewQuestion"] = relationship(back_populates="responses")
