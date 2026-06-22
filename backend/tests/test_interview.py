import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.contexts.tenant.models import Tenant
from src.contexts.auth.models import User
from src.contexts.intelligence.models import CandidateProfile
from src.core.enums import UserRole
from src.core.security import create_access_token


@pytest.mark.asyncio
async def test_interview_engine_lifecycle(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Verifies full interview session initialization, state transitions, responses, adaptivity, and details."""
    # 1. Setup Tenant and Recruiter token
    tenant = Tenant(id="acme_corp", name="Acme Corporation", status="ACTIVE")
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

    # 2. Setup Candidate User and Profile
    candidate_user = User(
        tenant_id="acme_corp",
        email="candidate_interview@example.com",
        hashed_password="dummy_password",
        role=UserRole.CANDIDATE,
        is_verified=True,
    )
    db_session.add(candidate_user)
    await db_session.commit()

    profile = CandidateProfile(
        tenant_id="acme_corp",
        user_id=candidate_user.id,
        experience_years=3.0,
        summary="Junior Backend Developer",
    )
    db_session.add(profile)
    await db_session.commit()

    candidate_id = str(profile.id)

    # 3. Create Interview Session (Initially in CREATED state)
    session_payload = {
        "candidate_id": candidate_id,
        "type": "TECHNICAL",
    }
    response = await client.post(
        "/api/v1/interviews", json=session_payload, headers=headers
    )
    assert response.status_code == 201
    session_data = response.json()["data"]
    assert session_data["status"] == "CREATED"
    assert session_data["type"] == "TECHNICAL"
    session_id = session_data["id"]

    # Try pausing a CREATED session (violates state machine transitions -> 400 Bad Request)
    response_pause_fail = await client.post(
        f"/api/v1/interviews/{session_id}/pause", headers=headers
    )
    assert response_pause_fail.status_code == 400
    assert "Cannot pause session" in response_pause_fail.json()["error"]["message"]

    # 4. Start the session -> transitions to RUNNING and automatically spawns the first question
    response_start = await client.post(
        f"/api/v1/interviews/{session_id}/start", headers=headers
    )
    assert response_start.status_code == 200
    started_data = response_start.json()["data"]
    assert started_data["status"] == "RUNNING"
    assert len(started_data["questions"]) == 1

    first_question = started_data["questions"][0]
    assert first_question["question_type"] == "PRIMARY"
    assert first_question["difficulty"] == "MEDIUM"
    assert first_question["order"] == 1

    # Try starting an already active/running session -> violates transitions
    response_start_again = await client.post(
        f"/api/v1/interviews/{session_id}/start", headers=headers
    )
    assert response_start_again.status_code == 400

    # 5. Submit candidate answer (long detailed response -> scores highly -> difficulty increases)
    response_payload = {
        "response_text": "I would use a thread-safe connection pool with optimized indices and serialize updates using mutex locks.",
    }
    response_submit = await client.post(
        f"/api/v1/interviews/{session_id}/response",
        json=response_payload,
        headers=headers,
    )
    assert response_submit.status_code == 200
    submit_data = response_submit.json()["data"]
    assert submit_data["feedback"]["score"] >= 4.0

    # Get details to inspect next question generation and adaptive difficulty increase
    response_get = await client.get(f"/api/v1/interviews/{session_id}", headers=headers)
    assert response_get.status_code == 200
    detail_data = response_get.json()["data"]
    assert (
        len(detail_data["questions"]) == 2
    )  # The 2nd question was automatically generated
    assert (
        detail_data["adaptive_state"]["current_difficulty"] == "HARD"
    )  # increased from MEDIUM to HARD
    assert "Evaluation Score" in detail_data["memory_summary"]

    # 6. Pause and Resume Session
    response_pause = await client.post(
        f"/api/v1/interviews/{session_id}/pause", headers=headers
    )
    assert response_pause.status_code == 200
    assert response_pause.json()["data"]["status"] == "PAUSED"

    # Try submitting answer while paused -> violates state machine
    response_submit_paused = await client.post(
        f"/api/v1/interviews/{session_id}/response",
        json={"response_text": "Lacking answer"},
        headers=headers,
    )
    assert response_submit_paused.status_code == 400

    response_resume = await client.post(
        f"/api/v1/interviews/{session_id}/resume", headers=headers
    )
    assert response_resume.status_code == 200
    assert response_resume.json()["data"]["status"] == "RUNNING"

    # 7. Submit poor response (triggers a FOLLOW_UP question and decreases difficulty)
    response_payload_mediocre = {
        "response_text": "I don't know, no idea really.",
    }
    response_submit2 = await client.post(
        f"/api/v1/interviews/{session_id}/response",
        json=response_payload_mediocre,
        headers=headers,
    )
    assert response_submit2.status_code == 200
    assert response_submit2.json()["data"]["feedback"]["score"] <= 3.0

    # Get details -> check that a FOLLOW_UP question was appended and difficulty adjusted down
    response_get2 = await client.get(
        f"/api/v1/interviews/{session_id}", headers=headers
    )
    detail_data2 = response_get2.json()["data"]
    assert len(detail_data2["questions"]) == 3
    assert detail_data2["questions"][2]["question_type"] == "FOLLOW_UP"
    assert (
        detail_data2["adaptive_state"]["current_difficulty"] == "MEDIUM"
    )  # decreased from HARD to MEDIUM

    # 8. Complete session explicitly
    response_complete = await client.post(
        f"/api/v1/interviews/{session_id}/complete", headers=headers
    )
    assert response_complete.status_code == 200
    assert response_complete.json()["data"]["status"] == "COMPLETED"
