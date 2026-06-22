import uuid
from src.contexts.interview.graph import (
    build_adaptive_interview_graph,
    InterviewState,
    CandidateContext,
)


def test_adaptive_interview_graph_lifecycle() -> None:
    """Verifies that the LangGraph state machine generates questions, interrupts, resumes, adapts difficulty, and evaluates."""
    # 1. Initialize Graph
    graph = build_adaptive_interview_graph()

    # Define session parameters
    session_id = uuid.uuid4()
    tenant_id = "acme_corp"
    context = CandidateContext(
        experience_years=4.5,
        summary="Experienced engineer.",
        skills_to_assess=["Python", "System Design", "Database Optimization"],
    )

    initial_state = InterviewState(
        session_id=session_id,
        tenant_id=tenant_id,
        candidate_context=context,
    )

    config = {"configurable": {"thread_id": str(session_id)}}

    # 2. Invoke Graph to trigger first question (runs until interrupt)
    res = graph.invoke(initial_state, config=config)

    # Check that a question has been generated and is pending answer
    assert res["current_question"] is not None
    assert len(res["questions"]) == 1
    assert res["questions"][0].question_type == "PRIMARY"
    assert res["questions"][0].difficulty == "MEDIUM"
    assert res["questions"][0].skill == "Python"
    assert res["is_completed"] is False

    # Verify that the graph interrupted before `receive_answer`
    state_snapshot = graph.get_state(config)
    assert state_snapshot.next == ("receive_answer",)

    # 3. Submit detailed answer (score should be high, leading to HARD difficulty next)
    graph.update_state(
        config,
        {
            "current_answer": "I would design a thread-safe caching system with write-through logic to ensure database consistency."
        },
        as_node="generate_question",
    )

    # Resume execution (passing None tells LangGraph to resume from checkpointer)
    res2 = graph.invoke(None, config=config)

    # Verification:
    # 1. Answer was evaluated and scored
    # 2. Next question was generated (which is PRIMARY since score was high)
    # 3. Difficulty adapted up to HARD
    # 4. Target skill moved to next in list (System Design)
    assert len(res2["questions"]) == 2
    assert res2["questions"][0].answer_text is not None
    assert res2["questions"][0].score >= 4.0

    assert res2["questions"][1].question_type == "PRIMARY"
    assert res2["questions"][1].difficulty == "HARD"
    assert res2["questions"][1].skill == "System Design"

    # Still interrupted for the new question
    state_snapshot2 = graph.get_state(config)
    assert state_snapshot2.next == ("receive_answer",)

    # 4. Submit weak answer (score should be low, leading to FOLLOW_UP and difficulty adjustment back to MEDIUM)
    graph.update_state(
        config, {"current_answer": "I don't know."}, as_node="generate_question"
    )

    res3 = graph.invoke(None, config=config)

    # Verification:
    # 1. Low score detected
    # 2. Weakness detected and logged
    # 3. Next question is a FOLLOW_UP
    # 4. Difficulty downgraded back to MEDIUM
    assert len(res3["questions"]) == 3
    assert res3["questions"][1].score <= 2.5
    assert len(res3["weaknesses"]) == 1
    assert "Gap in System Design" in res3["weaknesses"][0].title

    assert res3["questions"][2].question_type == "FOLLOW_UP"
    assert res3["questions"][2].difficulty == "MEDIUM"

    state_snapshot3 = graph.get_state(config)
    assert state_snapshot3.next == ("receive_answer",)

    # 5. Submit responses until session complete (e.g. 5 primary questions total)
    # Question 3: Follow-up. Submit response.
    graph.update_state(
        config,
        {"current_answer": "Here is a detailed elaboration of the architecture."},
        as_node="generate_question",
    )
    graph.invoke(None, config=config)

    # Question 4: Primary. Submit response.
    graph.update_state(
        config,
        {"current_answer": "Highly scaled database indexes description."},
        as_node="generate_question",
    )
    graph.invoke(None, config=config)

    # Question 5: Primary. Submit response.
    graph.update_state(
        config,
        {"current_answer": "Detailed description of sharding principles."},
        as_node="generate_question",
    )
    graph.invoke(None, config=config)

    # Question 6: Primary. Submit response.
    graph.update_state(
        config,
        {"current_answer": "Final answers on caching schemes."},
        as_node="generate_question",
    )
    res7 = graph.invoke(None, config=config)

    # Graph now determines overall score and sets is_completed = True
    assert res7["is_completed"] is True
    assert res7["overall_score"] is not None
    assert "completed" in res7["evaluation_summary"]
