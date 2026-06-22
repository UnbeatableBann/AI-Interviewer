import uuid
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver


class CandidateContext(BaseModel):
    """Context information about candidate's profile and target assessment skills."""

    experience_years: float = Field(default=0.0, ge=0.0)
    summary: str = Field(default="")
    skills_to_assess: List[str] = Field(default_factory=list)


class QuestionHistory(BaseModel):
    """Record of a question asked, the answer, and evaluation feedback."""

    question_text: str
    question_type: str = "PRIMARY"  # PRIMARY, FOLLOW_UP
    difficulty: str = "MEDIUM"  # EASY, MEDIUM, HARD
    skill: str
    answer_text: Optional[str] = None
    score: Optional[float] = None
    critique: Optional[str] = None


class WeaknessHistory(BaseModel):
    """Knowledge gaps or weaknesses identified during response analysis."""

    title: str
    description: str
    context: str  # Context source showing where it was observed


class InterviewState(BaseModel):
    """Top-level state for the LangGraph Interview state machine."""

    session_id: uuid.UUID
    tenant_id: str
    candidate_context: CandidateContext
    questions: List[QuestionHistory] = Field(default_factory=list)
    weaknesses: List[WeaknessHistory] = Field(default_factory=list)
    current_question: Optional[str] = None
    current_answer: Optional[str] = None
    current_difficulty: str = "MEDIUM"
    current_skill_index: int = 0
    consecutive_follow_ups: int = 0
    is_completed: bool = False
    evaluation_summary: Optional[str] = None
    overall_score: Optional[float] = None
    current_analysis: Optional[Dict[str, Any]] = None


# Mock helper generators to isolate testing without requiring active external LLM keys
def _mock_question_gen(
    skill: str, difficulty: str, is_follow_up: bool
) -> tuple[str, str]:
    if is_follow_up:
        return (
            f"Follow-up: How do you handle failure modes or performance limits when implementing {skill}?",
            "Detailed response on edge cases and failure mode mitigations.",
        )
    return (
        f"Explain how you design, implement, and optimize systems using {skill} at {difficulty} level.",
        f"Comprehensive description of {skill} application, architecture, and tradeoffs.",
    )


def _mock_evaluate(question: str, answer: str) -> tuple[float, str]:
    score = 4.0
    critique = (
        "Candidate's response is structured and covers the main architectural details."
    )
    words = len(answer.split())
    if words < 5:
        score = 2.0
        critique = "Response is too brief and lacks details."
    elif any(term in answer.lower() for term in ("don't know", "no idea", "unsure")):
        score = 1.0
        critique = "Candidate admitted lack of familiarity with concept."
    elif words > 25:
        score = 4.7
        critique = "Excellent, highly detailed explanation."
    return score, critique


# Node Definitions
def generate_question(state: InterviewState) -> Dict[str, Any]:
    """Generates the initial question or moves forward if one is already pending response."""
    if state.current_question and not state.current_answer:
        # Awaiting response for the current question
        return {}

    context = state.candidate_context
    skills = context.skills_to_assess or ["General Competency"]
    skill = skills[state.current_skill_index % len(skills)]

    question_text, expected = _mock_question_gen(
        skill, state.current_difficulty, is_follow_up=False
    )

    new_q = QuestionHistory(
        question_text=question_text,
        question_type="PRIMARY",
        difficulty=state.current_difficulty,
        skill=skill,
    )

    return {"current_question": question_text, "questions": state.questions + [new_q]}


def receive_answer(state: InterviewState) -> Dict[str, Any]:
    """Validates that candidate response is present before running evaluation."""
    if not state.current_answer:
        raise ValueError(
            "Cannot execute receive_answer without an active current_answer in state."
        )
    return {}


def analyze_answer(state: InterviewState) -> Dict[str, Any]:
    """Analyzes the response content, grading it and providing critiques."""
    if not state.questions:
        return {}

    last_q = state.questions[-1]
    score, critique = _mock_evaluate(last_q.question_text, state.current_answer or "")

    updated_q = last_q.model_copy(
        update={
            "answer_text": state.current_answer,
            "score": score,
            "critique": critique,
        }
    )

    questions = list(state.questions)
    questions[-1] = updated_q

    # Adapt difficulty level immediately based on score
    current_diff = state.current_difficulty
    if score >= 4.0:
        if current_diff == "EASY":
            next_diff = "MEDIUM"
        else:
            next_diff = "HARD"
    elif score < 3.0:
        if current_diff == "HARD":
            next_diff = "MEDIUM"
        else:
            next_diff = "EASY"
    else:
        next_diff = current_diff

    return {
        "questions": questions,
        "current_difficulty": next_diff,
        "current_analysis": {"score": score, "critique": critique},
    }


def detect_weakness(state: InterviewState) -> Dict[str, Any]:
    """Scours analysis results to check for knowledge gaps and register weakness logs."""
    analysis = state.current_analysis or {}
    score = analysis.get("score", 5.0)

    if score < 3.0:
        last_q = state.questions[-1] if state.questions else None
        skill = last_q.skill if last_q else "General"

        weakness = WeaknessHistory(
            title=f"Gap in {skill}",
            description=analysis.get("critique", "Response lacked analytical depth."),
            context=f"Question: {last_q.question_text if last_q else ''}",
        )
        return {"weaknesses": state.weaknesses + [weakness]}
    return {}


def generate_follow_up(state: InterviewState) -> Dict[str, Any]:
    """Spawns follow-up questions to probe candidate gaps further."""
    last_q = state.questions[-1] if state.questions else None
    skill = last_q.skill if last_q else "General"

    follow_up_text, expected = _mock_question_gen(
        skill, state.current_difficulty, is_follow_up=True
    )

    new_q = QuestionHistory(
        question_text=follow_up_text,
        question_type="FOLLOW_UP",
        difficulty=state.current_difficulty,
        skill=skill,
    )

    return {
        "current_question": follow_up_text,
        "questions": state.questions + [new_q],
        "current_answer": None,
        "consecutive_follow_ups": state.consecutive_follow_ups + 1,
    }


def escalate_depth(state: InterviewState) -> Dict[str, Any]:
    """Switches focus topic using the adapted difficulty level."""
    next_diff = state.current_difficulty

    next_skill_index = state.current_skill_index + 1
    skills = state.candidate_context.skills_to_assess or ["General Competency"]
    skill = skills[next_skill_index % len(skills)]

    question_text, expected = _mock_question_gen(skill, next_diff, is_follow_up=False)

    new_q = QuestionHistory(
        question_text=question_text,
        question_type="PRIMARY",
        difficulty=next_diff,
        skill=skill,
    )

    return {
        "current_skill_index": next_skill_index,
        "consecutive_follow_ups": 0,
        "current_question": question_text,
        "questions": state.questions + [new_q],
        "current_answer": None,
    }


def evaluate_session(state: InterviewState) -> Dict[str, Any]:
    """Compiles overall candidate performance and closes the session."""
    scores = [q.score for q in state.questions if q.score is not None]
    overall = sum(scores) / len(scores) if scores else 0.0

    summary = f"Interview completed with an overall score of {overall:.2f}/5.0. "
    if state.weaknesses:
        summary += f"Identified gaps: {', '.join([w.title for w in state.weaknesses])}."
    else:
        summary += "No critical knowledge gaps detected."

    return {
        "is_completed": True,
        "overall_score": overall,
        "evaluation_summary": summary,
    }


# Router Callback
def route_next_step(
    state: InterviewState,
) -> Literal["generate_follow_up", "escalate_depth", "evaluate_session"]:
    """Conditional router resolving the next graph transition node."""
    total_primary = sum(1 for q in state.questions if q.question_type == "PRIMARY")
    analysis = state.current_analysis or {}
    score = analysis.get("score", 5.0)

    # Cutoff limit of 5 primary questions (plus any follow-up probe)
    if total_primary >= 5 and state.consecutive_follow_ups == 0:
        return "evaluate_session"

    # Probing loop condition: score is mediocre and we haven't done consecutive follow-ups
    if score <= 3.5 and state.consecutive_follow_ups < 1:
        return "generate_follow_up"

    if total_primary >= 5:
        return "evaluate_session"

    return "escalate_depth"


def build_adaptive_interview_graph():
    """Builds and compiles the LangGraph StateGraph, attaching InMemory checkpointers and interrupts."""
    workflow = StateGraph(InterviewState)

    # 1. Register Nodes
    workflow.add_node("generate_question", generate_question)
    workflow.add_node("receive_answer", receive_answer)
    workflow.add_node("analyze_answer", analyze_answer)
    workflow.add_node("detect_weakness", detect_weakness)
    workflow.add_node("generate_follow_up", generate_follow_up)
    workflow.add_node("escalate_depth", escalate_depth)
    workflow.add_node("evaluate_session", evaluate_session)

    # 2. Add Transitions
    workflow.add_edge(START, "generate_question")
    workflow.add_edge("generate_question", "receive_answer")

    workflow.add_edge("receive_answer", "analyze_answer")
    workflow.add_edge("analyze_answer", "detect_weakness")

    workflow.add_conditional_edges(
        "detect_weakness",
        route_next_step,
        {
            "generate_follow_up": "generate_follow_up",
            "escalate_depth": "escalate_depth",
            "evaluate_session": "evaluate_session",
        },
    )

    workflow.add_edge("generate_follow_up", "receive_answer")
    workflow.add_edge("escalate_depth", "receive_answer")
    workflow.add_edge("evaluate_session", END)

    # Compile with MemorySaver checkpoints and halt interrupt execution hooks before answer ingestion
    checkpointer = MemorySaver()
    return workflow.compile(
        checkpointer=checkpointer, interrupt_before=["receive_answer"]
    )
