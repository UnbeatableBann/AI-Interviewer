from datetime import datetime, timezone
import uuid
from typing import List, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base


class Skill(Base):
    """Global skills dictionary defining domains and taxonomy categories."""

    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    category: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # TECHNICAL, SYSTEM_DESIGN, COMMUNICATION
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    candidate_links: Mapped[List["CandidateSkill"]] = relationship(
        back_populates="skill", cascade="all, delete-orphan"
    )


class CandidateProfile(Base):
    """Core Profile mapping candidates to tenants and aggregating intelligence insights."""

    __tablename__ = "candidate_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    resume_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    experience_years: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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

    # Relationships
    skills: Mapped[List["CandidateSkill"]] = relationship(
        back_populates="candidate", cascade="all, delete-orphan"
    )
    strengths: Mapped[List["Strength"]] = relationship(
        back_populates="candidate", cascade="all, delete-orphan"
    )
    weaknesses: Mapped[List["Weakness"]] = relationship(
        back_populates="candidate", cascade="all, delete-orphan"
    )
    progress_snapshots: Mapped[List["ProgressSnapshot"]] = relationship(
        back_populates="candidate", cascade="all, delete-orphan"
    )
    insights: Mapped[List["InterviewInsight"]] = relationship(
        back_populates="candidate", cascade="all, delete-orphan"
    )


class CandidateSkill(Base):
    """Association table mapping candidates to verified skill scores and evaluations."""

    __tablename__ = "candidate_skills"

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

    level: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )  # Rating score (0.0 to 5.0)
    confidence: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )  # Confidence score (0.0 to 1.0)
    evaluations_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_evaluated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    candidate: Mapped["CandidateProfile"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship(back_populates="candidate_links")


class Strength(Base):
    """Key highlights of outstanding candidate competencies identified during evaluations."""

    __tablename__ = "candidate_strengths"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    context_source: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )  # e.g., "Session X, Question Y"

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    candidate: Mapped["CandidateProfile"] = relationship(back_populates="strengths")


class Weakness(Base):
    """Development gaps and areas of concern identified during evaluation loops."""

    __tablename__ = "candidate_weaknesses"

    __tablename__ = "candidate_weaknesses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    context_source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    candidate: Mapped["CandidateProfile"] = relationship(back_populates="weaknesses")


class ProgressSnapshot(Base):
    """Longitudinal snapshot documenting candidate skill matrices over time."""

    __tablename__ = "candidate_progress_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    snapshot_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Store dynamic snapshot as serialized JSON text (e.g., {"Python": 4.2, "Communication": 3.8})
    skills_matrix: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    candidate: Mapped["CandidateProfile"] = relationship(
        back_populates="progress_snapshots"
    )


class InterviewInsight(Base):
    """Evaluative analytics capturing communication patterns and confidence metrics per session."""

    __tablename__ = "candidate_interview_insights"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False, index=True
    )  # Links to active interview session
    communication_score: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # e.g., 0.0 to 5.0
    confidence_score: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # e.g., 0.0 to 5.0
    technical_rating: Mapped[float] = mapped_column(Float, nullable=False)
    key_takeaways: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    candidate: Mapped["CandidateProfile"] = relationship(back_populates="insights")
