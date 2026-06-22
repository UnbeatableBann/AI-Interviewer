import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies.db import get_db
from src.api.dependencies.auth import get_current_user, CurrentUser, ScopeChecker
from src.contexts.interview.schemas import (
    InterviewSessionCreate,
    InterviewSessionResponse,
    InterviewSessionDetailResponse,
    InterviewResponseCreate,
    InterviewResponseResponse,
)
from src.contexts.interview.services import InterviewEngineService
from src.shared.schemas.responses import APIResponse
from src.core.exceptions import AuthorizationError

router = APIRouter(prefix="/interviews", tags=["interview-engine"])

recruiter_write = ScopeChecker(required_scopes=["recruiter:write"])
recruiter_read = ScopeChecker(required_scopes=["recruiter:read"])


def require_any_scope(allowed_scopes: List[str]):
    """Dynamic scope injection checking for multiple alternative scopes."""

    async def dependency(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if not any(scope in current_user.scopes for scope in allowed_scopes):
            raise AuthorizationError(
                f"Insufficient permissions. Required scope context: one of {allowed_scopes}."
            )
        return current_user

    return dependency


recruiter_or_candidate_read = require_any_scope(["recruiter:read", "candidate:read"])
recruiter_or_candidate_write = require_any_scope(["recruiter:write", "candidate:write"])


async def get_engine_service(
    db: AsyncSession = Depends(get_db),
) -> InterviewEngineService:
    """Dependency helper injecting active InterviewEngineService context."""
    return InterviewEngineService(db)


@router.post("", response_model=APIResponse[InterviewSessionResponse], status_code=201)
async def create_session(
    payload: InterviewSessionCreate,
    current_user: CurrentUser = Depends(recruiter_write),
    service: InterviewEngineService = Depends(get_engine_service),
) -> APIResponse[InterviewSessionResponse]:
    """Creates a new candidate interview session in CREATED state (Recruiter scope)."""
    session = await service.create_session(payload.candidate_id, payload.type)
    return APIResponse(
        success=True,
        data=InterviewSessionResponse.model_validate(session),
    )


@router.get("/{session_id}", response_model=APIResponse[InterviewSessionDetailResponse])
async def get_session(
    session_id: uuid.UUID,
    current_user: CurrentUser = Depends(recruiter_or_candidate_read),
    service: InterviewEngineService = Depends(get_engine_service),
) -> APIResponse[InterviewSessionDetailResponse]:
    """Retrieves full interview session details including history sequence (Recruiter/Candidate scope)."""
    session = await service.session_repo.get_session_with_relations(session_id)
    if not session:
        from src.core.exceptions import EntityNotFoundError

        raise EntityNotFoundError(f"Interview session '{session_id}' not found.")

    return APIResponse(
        success=True,
        data=InterviewSessionDetailResponse.model_validate(session),
    )


@router.post(
    "/{session_id}/start", response_model=APIResponse[InterviewSessionDetailResponse]
)
async def start_session(
    session_id: uuid.UUID,
    current_user: CurrentUser = Depends(recruiter_or_candidate_write),
    service: InterviewEngineService = Depends(get_engine_service),
) -> APIResponse[InterviewSessionDetailResponse]:
    """Transitions state machine to RUNNING and returns the first question (Recruiter/Candidate scope)."""
    session = await service.start_session(session_id)
    return APIResponse(
        success=True,
        data=InterviewSessionDetailResponse.model_validate(session),
    )


@router.post(
    "/{session_id}/pause", response_model=APIResponse[InterviewSessionResponse]
)
async def pause_session(
    session_id: uuid.UUID,
    current_user: CurrentUser = Depends(recruiter_write),
    service: InterviewEngineService = Depends(get_engine_service),
) -> APIResponse[InterviewSessionResponse]:
    """Pauses an active interview session, setting state to PAUSED (Recruiter scope)."""
    session = await service.pause_session(session_id)
    return APIResponse(
        success=True,
        data=InterviewSessionResponse.model_validate(session),
    )


@router.post(
    "/{session_id}/resume", response_model=APIResponse[InterviewSessionResponse]
)
async def resume_session(
    session_id: uuid.UUID,
    current_user: CurrentUser = Depends(recruiter_write),
    service: InterviewEngineService = Depends(get_engine_service),
) -> APIResponse[InterviewSessionResponse]:
    """Resumes a paused interview session back to RUNNING (Recruiter scope)."""
    session = await service.resume_session(session_id)
    return APIResponse(
        success=True,
        data=InterviewSessionResponse.model_validate(session),
    )


@router.post(
    "/{session_id}/complete", response_model=APIResponse[InterviewSessionResponse]
)
async def complete_session(
    session_id: uuid.UUID,
    current_user: CurrentUser = Depends(recruiter_write),
    service: InterviewEngineService = Depends(get_engine_service),
) -> APIResponse[InterviewSessionResponse]:
    """Closes an active/paused session setting status to COMPLETED (Recruiter scope)."""
    session = await service.complete_session(session_id)
    return APIResponse(
        success=True,
        data=InterviewSessionResponse.model_validate(session),
    )


@router.post("/{session_id}/fail", response_model=APIResponse[InterviewSessionResponse])
async def fail_session(
    session_id: uuid.UUID,
    current_user: CurrentUser = Depends(recruiter_write),
    service: InterviewEngineService = Depends(get_engine_service),
) -> APIResponse[InterviewSessionResponse]:
    """Sets session status to FAILED (Recruiter scope)."""
    session = await service.fail_session(session_id)
    return APIResponse(
        success=True,
        data=InterviewSessionResponse.model_validate(session),
    )


@router.post(
    "/{session_id}/response", response_model=APIResponse[InterviewResponseResponse]
)
async def submit_response(
    session_id: uuid.UUID,
    payload: InterviewResponseCreate,
    current_user: CurrentUser = Depends(recruiter_or_candidate_write),
    service: InterviewEngineService = Depends(get_engine_service),
) -> APIResponse[InterviewResponseResponse]:
    """Submits candidate transcript response, adapting difficulty and generating next question (Recruiter/Candidate scope)."""
    response = await service.submit_response(
        session_id=session_id,
        response_text=payload.response_text,
        audio_url=payload.audio_url,
    )
    return APIResponse(
        success=True,
        data=InterviewResponseResponse.model_validate(response),
    )
