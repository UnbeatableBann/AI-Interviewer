import uuid
import json
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.contexts.tenant.models import Tenant
from src.contexts.auth.models import User
from src.contexts.intelligence.models import ProgressSnapshot
from src.contexts.interview.models import InterviewSession
from src.contexts.evaluation.models import EvaluationReport
from src.core.enums import UserRole, InterviewType, InterviewStatus
from src.core.security import create_access_token


@pytest.mark.asyncio
async def test_candidate_intelligence_lifecycle_and_report(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Verifies profile creation, skill rolling calculations, insights recording and report generation."""
    # 1. Setup Tenant and Recruiter token
    tenant = Tenant(id="acme", name="Acme Corp", status="ACTIVE")
    db_session.add(tenant)
    await db_session.commit()

    recruiter_token = create_access_token(
        subject="rec_user_id",
        tenant_id="acme",
        scopes=["recruiter:write", "recruiter:read"],
    )
    headers = {
        "Authorization": f"Bearer {recruiter_token}",
        "X-Tenant-ID": "acme",
    }

    # 2. Provision Candidate user and profile
    candidate_user = User(
        tenant_id="acme",
        email="candidate_intel@example.com",
        hashed_password="dummy_password",
        role=UserRole.CANDIDATE,
        is_verified=True,
    )
    db_session.add(candidate_user)
    await db_session.commit()

    profile_payload = {
        "user_id": str(candidate_user.id),
        "resume_url": "https://storage/cv.pdf",
        "experience_years": 5.5,
        "summary": "Experienced python developer.",
    }

    response_profile = await client.post(
        "/api/v1/candidates", json=profile_payload, headers=headers
    )
    assert response_profile.status_code == 201
    candidate_id = response_profile.json()["data"]["id"]

    # 3. Create global skill definitions (Admin scope needed)
    admin_token = create_access_token(
        subject="admin_user_id",
        tenant_id="acme",
        scopes=["system:admin"],
    )
    admin_headers = {
        "Authorization": f"Bearer {admin_token}",
        "X-Tenant-ID": "acme",
    }

    skill_payload = {
        "name": "Python Development",
        "category": "TECHNICAL",
        "description": "Core python language features.",
    }
    response_skill = await client.post(
        "/api/v1/candidates/skills", json=skill_payload, headers=admin_headers
    )
    assert response_skill.status_code == 201
    skill_id = response_skill.json()["data"]["id"]

    # 4. Add/Update skill rating (triggers rolling averages)
    # Evaluation 1: score 4.0, confidence 0.8
    response_rating1 = await client.post(
        f"/api/v1/candidates/{candidate_id}/skills/{skill_id}?score=4.0&confidence=0.8",
        headers=headers,
    )
    assert response_rating1.status_code == 200
    assert response_rating1.json()["data"]["level"] == 4.0

    # Evaluation 2: score 5.0, confidence 1.0 -> rolling average level should become 4.5
    response_rating2 = await client.post(
        f"/api/v1/candidates/{candidate_id}/skills/{skill_id}?score=5.0&confidence=1.0",
        headers=headers,
    )
    assert response_rating2.status_code == 200
    assert response_rating2.json()["data"]["level"] == 4.5
    assert response_rating2.json()["data"]["evaluations_count"] == 2

    # 5. Log strengths and weaknesses
    strength_payload = {
        "title": "Clean Architecture",
        "description": "Exhibits solid understanding of decoupling use cases from routing layers.",
        "context_source": "Session 1",
    }
    response_strength = await client.post(
        f"/api/v1/candidates/{candidate_id}/strengths",
        json=strength_payload,
        headers=headers,
    )
    assert response_strength.status_code == 201

    weakness_payload = {
        "title": "Concurrency",
        "description": "Unfamiliar with python asyncio task group management.",
        "context_source": "Session 1",
    }
    response_weakness = await client.post(
        f"/api/v1/candidates/{candidate_id}/weaknesses",
        json=weakness_payload,
        headers=headers,
    )
    assert response_weakness.status_code == 201

    # 6. Record session insights (triggers automatic ProgressSnapshot)
    insight_payload = {
        "session_id": str(uuid.uuid4()),
        "communication_score": 4.0,
        "confidence_score": 4.5,
        "technical_rating": 4.2,
        "key_takeaways": "Excellent problem solver. Needs slight coaching on asynchronous control flows.",
    }
    response_insight = await client.post(
        f"/api/v1/candidates/{candidate_id}/insights",
        json=insight_payload,
        headers=headers,
    )
    assert response_insight.status_code == 201

    # Verify progress snapshot was captured and serialized
    stmt_snap = select(ProgressSnapshot).where(
        ProgressSnapshot.candidate_id == uuid.UUID(candidate_id)
    )
    res_snap = await db_session.execute(stmt_snap)
    snapshot = res_snap.scalars().first()
    assert snapshot is not None
    assert snapshot.overall_score == 4.5  # Only 1 skill exists, with level 4.5
    matrix = json.loads(snapshot.skills_matrix)
    assert matrix["Python Development"] == 4.5

    # 7. Generate Candidate Intelligence Report
    response_report = await client.get(
        f"/api/v1/candidates/{candidate_id}/intelligence", headers=headers
    )
    assert response_report.status_code == 200
    report_data = response_report.json()["data"]

    # Verify report segments are fully pre-loaded
    assert report_data["profile"]["summary"] == "Experienced python developer."
    assert len(report_data["skills"]) == 1
    assert report_data["skills"][0]["skill"]["name"] == "Python Development"
    assert len(report_data["strengths"]) == 1
    assert report_data["strengths"][0]["title"] == "Clean Architecture"
    assert len(report_data["weaknesses"]) == 1
    assert report_data["weaknesses"][0]["title"] == "Concurrency"
    assert len(report_data["insights"]) == 1
    assert len(report_data["progress_snapshots"]) == 1


@pytest.mark.asyncio
async def test_candidate_long_term_memory(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Verifies retrieval of full candidate long-term memory including timeline, graph, and evolution."""
    # 1. Setup Tenant and Recruiter token
    tenant = Tenant(id="acme_mem", name="Acme Memory Corp", status="ACTIVE")
    db_session.add(tenant)
    await db_session.commit()

    recruiter_token = create_access_token(
        subject="rec_user_mem",
        tenant_id="acme_mem",
        scopes=["recruiter:write", "recruiter:read"],
    )
    headers = {
        "Authorization": f"Bearer {recruiter_token}",
        "X-Tenant-ID": "acme_mem",
    }

    # 2. Setup Candidate user and profile
    candidate_user = User(
        tenant_id="acme_mem",
        email="candidate_mem@example.com",
        hashed_password="dummy_password",
        role=UserRole.CANDIDATE,
        is_verified=True,
    )
    db_session.add(candidate_user)
    await db_session.commit()

    profile_payload = {
        "user_id": str(candidate_user.id),
        "resume_url": "https://storage/cv_mem.pdf",
        "experience_years": 4.5,
        "summary": "Fullstack python developer.",
    }
    response_profile = await client.post(
        "/api/v1/candidates", json=profile_payload, headers=headers
    )
    assert response_profile.status_code == 201
    candidate_id = response_profile.json()["data"]["id"]

    # 3. Setup Skill definitions and add evaluation
    admin_token = create_access_token(
        subject="admin_user_mem",
        tenant_id="acme_mem",
        scopes=["system:admin"],
    )
    admin_headers = {
        "Authorization": f"Bearer {admin_token}",
        "X-Tenant-ID": "acme_mem",
    }
    skill_payload = {
        "name": "Python Language",
        "category": "TECHNICAL",
        "description": "Backend coding capabilities.",
    }
    response_skill = await client.post(
        "/api/v1/candidates/skills", json=skill_payload, headers=admin_headers
    )
    assert response_skill.status_code == 201
    skill_id = response_skill.json()["data"]["id"]

    # Evaluate skill level
    await client.post(
        f"/api/v1/candidates/{candidate_id}/skills/{skill_id}?score=4.0&confidence=0.9",
        headers=headers,
    )

    # Log Strengths & Weaknesses
    await client.post(
        f"/api/v1/candidates/{candidate_id}/strengths",
        json={"title": "Fast Learner", "description": "Quick to adopt new runtimes"},
        headers=headers,
    )
    await client.post(
        f"/api/v1/candidates/{candidate_id}/weaknesses",
        json={
            "title": "CSS Layouts",
            "description": "Fails simple flexbox align checks",
        },
        headers=headers,
    )

    # 4. Direct SQL insertions for Interview and Evaluation records to represent session history
    session = InterviewSession(
        tenant_id="acme_mem",
        candidate_id=uuid.UUID(candidate_id),
        type=InterviewType.TECHNICAL,
        status=InterviewStatus.COMPLETED,
        memory_summary="Detailed technical discussion.",
        adaptive_state={"current_difficulty": "HARD"},
    )
    db_session.add(session)
    await db_session.commit()

    evaluation = EvaluationReport(
        tenant_id="acme_mem",
        session_id=session.id,
        overall_score=4.2,
        technical_accuracy_score=4.5,
        communication_score=4.0,
        depth_score=4.2,
        problem_solving_score=4.5,
        confidence_score=4.0,
        completeness_score=4.0,
        summary="Outstanding accuracy in systems architecture queries.",
        faithfulness_score=1.0,
        rubric_used={
            "Problem Solving": "Score 4.5: Solved design with cache isolation"
        },
        extracted_evidence=[
            {"evidence": "Candidate explained thread safety using locks"}
        ],
    )
    db_session.add(evaluation)
    await db_session.commit()

    # Log insights (triggers snapshots capture)
    insight_payload = {
        "session_id": str(session.id),
        "communication_score": 4.5,
        "confidence_score": 4.0,
        "technical_rating": 4.2,
        "key_takeaways": "Strong coding. High growth velocity.",
    }
    await client.post(
        f"/api/v1/candidates/{candidate_id}/insights",
        json=insight_payload,
        headers=headers,
    )

    # 5. Query candidate long-term memory
    response_memory = await client.get(
        f"/api/v1/candidates/{candidate_id}/memory", headers=headers
    )
    assert response_memory.status_code == 200
    memory_data = response_memory.json()["data"]

    # Verify Timeline
    timeline = memory_data["timeline"]
    assert len(timeline) >= 4  # Includes Created, Ended, Evaluation, Insight, Snapshot
    # Check chronological ordering
    timestamps = [t["timestamp"] for t in timeline]
    assert sorted(timestamps) == timestamps
    assert timeline[0]["event_type"] == "INTERVIEW"

    # Verify Skill Evolution
    evolution = memory_data["skill_evolution"]
    assert "Python Language" in evolution
    assert len(evolution["Python Language"]) == 1
    assert evolution["Python Language"][0]["level"] == 4.0

    # Verify Knowledge Graph
    graph = memory_data["knowledge_graph"]
    # Check that candidate, skill, interview, evaluation nodes are present
    types = {n["type"] for n in graph["nodes"]}
    assert "CANDIDATE" in types
    assert "SKILL" in types
    assert "INTERVIEW" in types
    assert "EVALUATION" in types
    assert "STRENGTH" in types
    assert "WEAKNESS" in types

    relations = {e["relation"] for e in graph["edges"]}
    assert "POSSESSES" in relations
    assert "PARTICIPATED_IN" in relations
    assert "GENERATED_EVALUATION" in relations

    # Verify original records are directly included
    assert len(memory_data["interviews"]) == 1
    assert len(memory_data["evaluations"]) == 1
    assert len(memory_data["insights"]) == 1
    assert memory_data["interviews"][0]["id"] == str(session.id)
    assert memory_data["evaluations"][0]["overall_score"] == 4.2
