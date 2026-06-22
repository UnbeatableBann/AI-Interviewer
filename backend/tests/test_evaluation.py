import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.contexts.tenant.models import Tenant
from src.contexts.auth.models import User
from src.contexts.intelligence.models import CandidateProfile, Skill, CandidateSkill
from src.contexts.interview.models import (
    InterviewSession,
    InterviewQuestion,
    InterviewResponse,
)
from src.core.enums import UserRole, InterviewType, InterviewStatus
from src.core.security import create_access_token


@pytest.mark.asyncio
async def test_evaluation_engine_and_skill_gaps(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Verifies that the evaluation engine correctly scores, detects hallucinations, calculates gaps, and yields reports."""
    # 1. Setup Tenant and Recruiter token
    tenant = Tenant(id="acme_corp", name="Acme Corp", status="ACTIVE")
    db_session.add(tenant)
    await db_session.commit()

    recruiter_token = create_access_token(
        subject="rec_user",
        tenant_id="acme_corp",
        scopes=["recruiter:write", "recruiter:read"],
    )
    headers = {
        "Authorization": f"Bearer {recruiter_token}",
        "X-Tenant-ID": "acme_corp",
    }

    # 2. Setup Candidate Profile
    candidate_user = User(
        tenant_id="acme_corp",
        email="candidate_eval@example.com",
        hashed_password="dummy_password",
        role=UserRole.CANDIDATE,
        is_verified=True,
    )
    db_session.add(candidate_user)
    await db_session.commit()

    profile = CandidateProfile(
        tenant_id="acme_corp",
        user_id=candidate_user.id,
        experience_years=4.0,
        summary="Mid Level Engineer",
    )
    db_session.add(profile)
    await db_session.commit()

    candidate_id = profile.id

    # 3. Setup Global Skill taxonomy definition
    skill = Skill(
        name="Python",
        category="TECHNICAL",
        description="Python runtime characteristics.",
    )
    db_session.add(skill)
    await db_session.commit()

    # Pre-configure candidate skill rating of 3.0 level
    cand_skill = CandidateSkill(
        tenant_id="acme_corp",
        candidate_id=candidate_id,
        skill_id=skill.id,
        level=3.0,
        confidence=0.8,
        evaluations_count=2,
    )
    db_session.add(cand_skill)
    await db_session.commit()

    # 4. Setup Completed Interview Session
    session = InterviewSession(
        tenant_id="acme_corp",
        candidate_id=candidate_id,
        type=InterviewType.TECHNICAL,
        status=InterviewStatus.COMPLETED,  # Session must be COMPLETED to evaluate
        memory_summary="Interview session completed.",
    )
    db_session.add(session)
    await db_session.commit()

    question = InterviewQuestion(
        tenant_id="acme_corp",
        session_id=session.id,
        question_text="Explain Python multithreading concurrency options.",
        difficulty="MEDIUM",
        skills_assessed=["Python"],
    )
    db_session.add(question)
    await db_session.commit()

    # Answer contains deliberate GIL hallucination claims to test detector
    response = InterviewResponse(
        tenant_id="acme_corp",
        session_id=session.id,
        question_id=question.id,
        response_text="Python supports native concurrent multithreading. Multiple threads can bytecode concurrent execute without locking issues.",
    )
    db_session.add(response)
    await db_session.commit()

    # 5. Trigger session evaluation
    payload = {
        "session_id": str(session.id),
        "required_skill_levels": {"Python": 4.5},
    }
    response_eval = await client.post(
        "/api/v1/evaluations", json=payload, headers=headers
    )
    assert response_eval.status_code == 201
    eval_data = response_eval.json()["data"]

    # Assert 6 dimensions exist and score properly
    assert eval_data["overall_score"] > 0
    assert eval_data["technical_accuracy_score"] > 0
    assert eval_data["communication_score"] > 0
    assert eval_data["depth_score"] > 0
    assert eval_data["problem_solving_score"] > 0
    assert eval_data["confidence_score"] > 0
    assert eval_data["completeness_score"] > 0

    # Assert Hallucination Detection matches Python thread spec claim
    halls = eval_data["hallucinations_detected"]
    assert len(halls) == 1
    assert halls[0]["severity"] == "HIGH"
    assert "GIL" in halls[0]["critique"]

    # Assert Faithfulness validation decreases due to hallucination
    assert eval_data["faithfulness_score"] == 0.8
    assert len(eval_data["extracted_evidence"]) == 1

    # 6. Fetch Evaluation Report via GET report endpoint
    response_report = await client.get(
        f"/api/v1/evaluations/reports/{session.id}", headers=headers
    )
    assert response_report.status_code == 200
    assert response_report.json()["data"]["id"] == eval_data["id"]

    # 7. Fetch Candidate Skill Gap Report details
    response_gaps = await client.get(
        f"/api/v1/evaluations/gaps/{candidate_id}", headers=headers
    )
    assert response_gaps.status_code == 200
    gaps_list = response_gaps.json()["data"]
    assert len(gaps_list) == 1

    # Required 4.5, Current 3.0 -> Gap 1.5
    assert gaps_list[0]["current_level"] == 3.0
    assert gaps_list[0]["required_level"] == 4.5
    assert gaps_list[0]["gap"] == 1.5
    assert "Core training required" in gaps_list[0]["recommendations"]
    assert gaps_list[0]["skill"]["name"] == "Python"
