import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies.db import get_db
from src.api.dependencies.auth import ScopeChecker, CurrentUser
from src.contexts.evaluation.schemas import (
    EvaluationCreatePayload,
    EvaluationReportResponse,
    SkillGapReportResponse,
)
from src.contexts.evaluation.services import EvaluationEngineService
from src.shared.schemas.responses import APIResponse

router = APIRouter(prefix="/evaluations", tags=["evaluation-engine"])

recruiter_write = ScopeChecker(required_scopes=["recruiter:write"])
recruiter_read = ScopeChecker(required_scopes=["recruiter:read"])


async def get_eval_service(
    db: AsyncSession = Depends(get_db),
) -> EvaluationEngineService:
    """Dependency helper injecting active EvaluationEngineService context."""
    return EvaluationEngineService(db)


@router.post("", response_model=APIResponse[EvaluationReportResponse], status_code=201)
async def evaluate_session(
    payload: EvaluationCreatePayload,
    current_user: CurrentUser = Depends(recruiter_write),
    service: EvaluationEngineService = Depends(get_eval_service),
) -> APIResponse[EvaluationReportResponse]:
    """Triggers evaluations scoring, extracting evidence quotes and compiling reports (Recruiter scope)."""
    report = await service.evaluate_session(
        payload.session_id, payload.required_skill_levels
    )
    return APIResponse(
        success=True,
        data=EvaluationReportResponse.model_validate(report),
    )


@router.get(
    "/reports/{session_id}", response_model=APIResponse[EvaluationReportResponse]
)
async def get_evaluation_report(
    session_id: uuid.UUID,
    current_user: CurrentUser = Depends(recruiter_read),
    service: EvaluationEngineService = Depends(get_eval_service),
) -> APIResponse[EvaluationReportResponse]:
    """Retrieves generated evaluation scores report for a session (Recruiter scope)."""
    report = await service.report_repo.get_by_session_id(session_id)
    if not report:
        from src.core.exceptions import EntityNotFoundError

        raise EntityNotFoundError(
            f"Evaluation report for session '{session_id}' not found."
        )

    return APIResponse(
        success=True,
        data=EvaluationReportResponse.model_validate(report),
    )


@router.get(
    "/gaps/{candidate_id}", response_model=APIResponse[List[SkillGapReportResponse]]
)
async def get_skill_gaps(
    candidate_id: uuid.UUID,
    current_user: CurrentUser = Depends(recruiter_read),
    service: EvaluationEngineService = Depends(get_eval_service),
) -> APIResponse[List[SkillGapReportResponse]]:
    """Loads all identified skill gaps and recommendations lists for a candidate (Recruiter scope)."""
    gaps = await service.gap_repo.get_by_candidate_id(candidate_id)
    return APIResponse(
        success=True,
        data=[SkillGapReportResponse.model_validate(g) for g in gaps],
    )
