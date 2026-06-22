import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies.db import get_db
from src.api.dependencies.auth import ScopeChecker, CurrentUser
from src.contexts.intelligence.schemas import (
    SkillCreate,
    SkillResponse,
    CandidateProfileCreate,
    CandidateProfileResponse,
    CandidateProfileUpdate,
    CandidateSkillResponse,
    StrengthCreate,
    StrengthResponse,
    WeaknessCreate,
    WeaknessResponse,
    InterviewInsightCreate,
    InterviewInsightResponse,
    CandidateIntelligenceReport,
    CandidateMemoryResponse,
)
from src.contexts.intelligence.services import CandidateIntelligenceService
from src.shared.schemas.responses import APIResponse

router = APIRouter(prefix="/candidates", tags=["candidate-intelligence"])

# Scope definitions
recruiter_write = ScopeChecker(required_scopes=["recruiter:write"])
recruiter_read = ScopeChecker(required_scopes=["recruiter:read"])
admin_scope = ScopeChecker(required_scopes=["system:admin"])


async def get_intel_service(
    db: AsyncSession = Depends(get_db),
) -> CandidateIntelligenceService:
    return CandidateIntelligenceService(db)


@router.post("/skills", response_model=APIResponse[SkillResponse], status_code=201)
async def define_global_skill(
    payload: SkillCreate,
    current_user: CurrentUser = Depends(admin_scope),
    service: CandidateIntelligenceService = Depends(get_intel_service),
) -> APIResponse[SkillResponse]:
    """Registers a global skill definition taxonomy in the platform dictionary (Admin scope)."""
    skill = await service.create_global_skill(payload)
    return APIResponse(
        success=True,
        data=SkillResponse.model_validate(skill),
    )


@router.post("", response_model=APIResponse[CandidateProfileResponse], status_code=201)
async def provision_profile(
    payload: CandidateProfileCreate,
    current_user: CurrentUser = Depends(recruiter_write),
    service: CandidateIntelligenceService = Depends(get_intel_service),
) -> APIResponse[CandidateProfileResponse]:
    """Provisions a new candidate profile mapping to active tenant context (Recruiter scope)."""
    profile = await service.create_candidate_profile(
        user_id=payload.user_id,
        resume_url=payload.resume_url,
        experience_years=payload.experience_years,
        summary=payload.summary,
    )
    return APIResponse(
        success=True,
        data=CandidateProfileResponse.model_validate(profile),
    )


@router.put("/{candidate_id}", response_model=APIResponse[CandidateProfileResponse])
async def update_profile(
    candidate_id: uuid.UUID,
    payload: CandidateProfileUpdate,
    current_user: CurrentUser = Depends(recruiter_write),
    service: CandidateIntelligenceService = Depends(get_intel_service),
) -> APIResponse[CandidateProfileResponse]:
    """Updates candidate CV summary, experience and links (Recruiter scope)."""
    profile = await service.update_candidate_profile(candidate_id, payload)
    return APIResponse(
        success=True,
        data=CandidateProfileResponse.model_validate(profile),
    )


@router.get(
    "/{candidate_id}/intelligence",
    response_model=APIResponse[CandidateIntelligenceReport],
)
async def get_intelligence_report(
    candidate_id: uuid.UUID,
    current_user: CurrentUser = Depends(recruiter_read),
    service: CandidateIntelligenceService = Depends(get_intel_service),
) -> APIResponse[CandidateIntelligenceReport]:
    """Loads the fully aggregated Candidate Intelligence Report profile (Recruiter scope)."""
    report = await service.get_intelligence_report(candidate_id)
    return APIResponse(
        success=True,
        data=report,
    )


@router.post(
    "/{candidate_id}/skills/{skill_id}",
    response_model=APIResponse[CandidateSkillResponse],
)
async def evaluate_candidate_skill(
    candidate_id: uuid.UUID,
    skill_id: uuid.UUID,
    score: float,
    confidence: float,
    current_user: CurrentUser = Depends(recruiter_write),
    service: CandidateIntelligenceService = Depends(get_intel_service),
) -> APIResponse[CandidateSkillResponse]:
    """Updates dynamic skill scores mapping confidence weights (Recruiter scope)."""
    cand_skill = await service.add_or_update_candidate_skill(
        candidate_id, skill_id, score, confidence
    )
    return APIResponse(
        success=True,
        data=CandidateSkillResponse.model_validate(cand_skill),
    )


@router.post(
    "/{candidate_id}/strengths",
    response_model=APIResponse[StrengthResponse],
    status_code=201,
)
async def add_strength(
    candidate_id: uuid.UUID,
    payload: StrengthCreate,
    current_user: CurrentUser = Depends(recruiter_write),
    service: CandidateIntelligenceService = Depends(get_intel_service),
) -> APIResponse[StrengthResponse]:
    """Logs a strength competency highlight against candidate (Recruiter scope)."""
    strength = await service.add_strength(candidate_id, payload)
    return APIResponse(
        success=True,
        data=StrengthResponse.model_validate(strength),
    )


@router.post(
    "/{candidate_id}/weaknesses",
    response_model=APIResponse[WeaknessResponse],
    status_code=201,
)
async def add_weakness(
    candidate_id: uuid.UUID,
    payload: WeaknessCreate,
    current_user: CurrentUser = Depends(recruiter_write),
    service: CandidateIntelligenceService = Depends(get_intel_service),
) -> APIResponse[WeaknessResponse]:
    """Logs a weakness development gap against candidate (Recruiter scope)."""
    weakness = await service.add_weakness(candidate_id, payload)
    return APIResponse(
        success=True,
        data=WeaknessResponse.model_validate(weakness),
    )


@router.post(
    "/{candidate_id}/insights",
    response_model=APIResponse[InterviewInsightResponse],
    status_code=201,
)
async def record_insight(
    candidate_id: uuid.UUID,
    payload: InterviewInsightCreate,
    current_user: CurrentUser = Depends(recruiter_write),
    service: CandidateIntelligenceService = Depends(get_intel_service),
) -> APIResponse[InterviewInsightResponse]:
    """Records session parameters and captures dynamic longitudinal snapshots (Recruiter scope)."""
    insight = await service.record_interview_insight(candidate_id, payload)
    return APIResponse(
        success=True,
        data=InterviewInsightResponse.model_validate(insight),
    )


@router.get(
    "/{candidate_id}/memory",
    response_model=APIResponse[CandidateMemoryResponse],
)
async def get_candidate_memory(
    candidate_id: uuid.UUID,
    current_user: CurrentUser = Depends(recruiter_read),
    service: CandidateIntelligenceService = Depends(get_intel_service),
) -> APIResponse[CandidateMemoryResponse]:
    """Retrieves full candidate long-term memory including timeline milestones, skill evolution lists, and connection graphs."""
    memory = await service.get_candidate_long_term_memory(candidate_id)
    return APIResponse(
        success=True,
        data=memory,
    )
