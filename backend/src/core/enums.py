from enum import Enum


class UserRole(str, Enum):
    """User authorization levels allowed on the platform."""

    ADMIN = "ADMIN"
    RECRUITER = "RECRUITER"
    CANDIDATE = "CANDIDATE"


class SessionStatus(str, Enum):
    """Lifecyle state machine statuses for an interview session."""

    SCHEDULED = "SCHEDULED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    EVALUATING = "EVALUATING"
    FINISHED = "FINISHED"


class SpeakerType(str, Enum):
    """Dialogue speaker roles in transcript logs."""

    CANDIDATE = "CANDIDATE"
    AI = "AI"


class InterviewType(str, Enum):
    """Supported types of interviews in the platform."""

    TECHNICAL = "TECHNICAL"
    HR = "HR"
    SYSTEM_DESIGN = "SYSTEM_DESIGN"


class InterviewStatus(str, Enum):
    """Lifecycle state machine statuses for an interview session."""

    CREATED = "CREATED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
