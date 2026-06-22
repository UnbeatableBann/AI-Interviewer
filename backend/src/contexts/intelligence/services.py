import json
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions import EntityNotFoundError, BusinessRuleValidationError
from src.contexts.interview.models import InterviewSession
from src.contexts.evaluation.models import EvaluationReport
from src.contexts.intelligence.models import (
    Skill,
    CandidateProfile,
    CandidateSkill,
    Strength,
    Weakness,
    ProgressSnapshot,
    InterviewInsight,
)
from src.contexts.intelligence.repositories import (
    SkillRepository,
    CandidateProfileRepository,
    CandidateSkillRepository,
    StrengthRepository,
    WeaknessRepository,
    ProgressSnapshotRepository,
    InterviewInsightRepository,
)
from src.contexts.intelligence.schemas import (
    SkillCreate,
    CandidateProfileUpdate,
    StrengthCreate,
    WeaknessCreate,
    InterviewInsightCreate,
    CandidateIntelligenceReport,
    CandidateProfileResponse,
    CandidateSkillResponse,
    StrengthResponse,
    WeaknessResponse,
    InterviewInsightResponse,
    ProgressSnapshotResponse,
    SkillResponse,
    CandidateMemoryResponse,
    TimelineEvent,
    GraphNode,
    GraphEdge,
    KnowledgeGraph,
)


class CandidateIntelligenceService:
    """Orchestrates candidate profile construction, skill matrix growth, and snapshotting."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.skill_repo = SkillRepository(db)
        self.profile_repo = CandidateProfileRepository(db)
        self.cand_skill_repo = CandidateSkillRepository(db)
        self.strength_repo = StrengthRepository(db)
        self.weakness_repo = WeaknessRepository(db)
        self.snapshot_repo = ProgressSnapshotRepository(db)
        self.insight_repo = InterviewInsightRepository(db)

    async def create_global_skill(self, schema: SkillCreate) -> Skill:
        """Registers a global skill definition taxonomy."""
        existing = await self.skill_repo.get_by_name(schema.name)
        if existing:
            raise BusinessRuleValidationError(
                f"Skill '{schema.name}' is already defined."
            )

        skill = Skill(
            name=schema.name, category=schema.category, description=schema.description
        )
        res = await self.skill_repo.create(skill)
        await self.db.commit()
        return res

    async def create_candidate_profile(
        self,
        user_id: uuid.UUID,
        resume_url: Optional[str] = None,
        experience_years: Optional[float] = None,
        summary: Optional[str] = None,
    ) -> CandidateProfile:
        """Provisions a new candidate profile mapping to active tenant context."""
        existing = await self.profile_repo.get_by_user_id(user_id)
        if existing:
            raise BusinessRuleValidationError(
                "Candidate profile already exists for this user."
            )

        profile = CandidateProfile(
            user_id=user_id,
            resume_url=resume_url,
            experience_years=experience_years,
            summary=summary,
        )
        res = await self.profile_repo.create(profile)
        await self.db.commit()
        return res

    async def update_candidate_profile(
        self,
        candidate_id: uuid.UUID,
        schema: CandidateProfileUpdate,
    ) -> CandidateProfile:
        """Updates candidate CV summary, experience and links."""
        profile = await self.profile_repo.get_by_id(candidate_id)
        if not profile:
            raise EntityNotFoundError(f"Candidate profile '{candidate_id}' not found.")

        if schema.resume_url is not None:
            profile.resume_url = schema.resume_url
        if schema.experience_years is not None:
            profile.experience_years = schema.experience_years
        if schema.summary is not None:
            profile.summary = schema.summary

        await self.profile_repo.update(profile)
        await self.db.commit()
        return profile

    async def add_or_update_candidate_skill(
        self,
        candidate_id: uuid.UUID,
        skill_id: uuid.UUID,
        score: float,
        confidence: float,
    ) -> CandidateSkill:
        """Updates skill scores using a rolling average weight based on test counts."""
        # Validate that global skill definition exists
        skill_def = await self.skill_repo.get_by_id(skill_id)
        if not skill_def:
            raise EntityNotFoundError(f"Skill taxonomy '{skill_id}' not found.")

        cand_skill = await self.cand_skill_repo.get_by_candidate_and_skill(
            candidate_id, skill_id
        )
        if cand_skill:
            # Recalculate rolling average to model skill progression
            count = cand_skill.evaluations_count
            cand_skill.level = ((cand_skill.level * count) + score) / (count + 1)
            cand_skill.confidence = ((cand_skill.confidence * count) + confidence) / (
                count + 1
            )
            cand_skill.evaluations_count += 1
            cand_skill.last_evaluated = datetime.now(timezone.utc)
            cand_skill.skill = skill_def
            res = await self.cand_skill_repo.create(cand_skill)
        else:
            cand_skill = CandidateSkill(
                candidate_id=candidate_id,
                skill_id=skill_id,
                level=score,
                confidence=confidence,
                evaluations_count=1,
                skill=skill_def,
            )
            res = await self.cand_skill_repo.create(cand_skill)

        await self.db.commit()
        return res

    async def add_strength(
        self, candidate_id: uuid.UUID, schema: StrengthCreate
    ) -> Strength:
        """Logs a strength competency record against candidate."""
        strength = Strength(
            candidate_id=candidate_id,
            title=schema.title,
            description=schema.description,
            context_source=schema.context_source,
        )
        res = await self.strength_repo.create(strength)
        await self.db.commit()
        return res

    async def add_weakness(
        self, candidate_id: uuid.UUID, schema: WeaknessCreate
    ) -> Weakness:
        """Logs a weakness development gap against candidate."""
        weakness = Weakness(
            candidate_id=candidate_id,
            title=schema.title,
            description=schema.description,
            context_source=schema.context_source,
        )
        res = await self.weakness_repo.create(weakness)
        await self.db.commit()
        return res

    async def record_interview_insight(
        self,
        candidate_id: uuid.UUID,
        schema: InterviewInsightCreate,
    ) -> InterviewInsight:
        """Records overall interview session parameters and creates progress snapshots."""
        # 1. Save insight details
        insight = InterviewInsight(
            candidate_id=candidate_id,
            session_id=schema.session_id,
            communication_score=schema.communication_score,
            confidence_score=schema.confidence_score,
            technical_rating=schema.technical_rating,
            key_takeaways=schema.key_takeaways,
        )
        res_insight = await self.insight_repo.create(insight)

        # 2. Automatically capture ProgressSnapshot
        # Load all updated skills for the candidate to compile matrix
        profile = await self.profile_repo.get_profile_with_relations(candidate_id)
        if not profile:
            raise EntityNotFoundError(f"Candidate profile '{candidate_id}' not found.")

        matrix = {}
        total_score = 0.0
        for cs in profile.skills:
            matrix[cs.skill.name] = cs.level
            total_score += cs.level

        overall = (total_score / len(profile.skills)) if profile.skills else 0.0

        snapshot = ProgressSnapshot(
            candidate_id=candidate_id,
            overall_score=overall,
            skills_matrix=json.dumps(matrix),
        )
        await self.snapshot_repo.create(snapshot)
        await self.db.commit()

        return res_insight

    async def get_intelligence_report(
        self, candidate_id: uuid.UUID
    ) -> CandidateIntelligenceReport:
        """Loads relationships pre-fetched and serializes the complete intelligence report."""
        profile = await self.profile_repo.get_profile_with_relations(candidate_id)
        if not profile:
            raise EntityNotFoundError(f"Candidate profile '{candidate_id}' not found.")

        # Serialize children models cleanly
        profile_res = CandidateProfileResponse.model_validate(profile)

        skills_res = [
            CandidateSkillResponse(
                id=s.id,
                level=s.level,
                confidence=s.confidence,
                evaluations_count=s.evaluations_count,
                last_evaluated=s.last_evaluated,
                skill=SkillResponse.model_validate(s.skill),
            )
            for s in profile.skills
        ]

        strengths_res = [
            StrengthResponse.model_validate(st) for st in profile.strengths
        ]
        weaknesses_res = [
            WeaknessResponse.model_validate(w) for w in profile.weaknesses
        ]
        insights_res = [
            InterviewInsightResponse.model_validate(i) for i in profile.insights
        ]
        snapshots_res = [
            ProgressSnapshotResponse.model_validate(sp)
            for sp in profile.progress_snapshots
        ]

        return CandidateIntelligenceReport(
            profile=profile_res,
            skills=skills_res,
            strengths=strengths_res,
            weaknesses=weaknesses_res,
            insights=insights_res,
            progress_snapshots=snapshots_res,
        )

    async def get_candidate_long_term_memory(
        self, candidate_id: uuid.UUID
    ) -> CandidateMemoryResponse:
        """Assembles timelines, connection graphs, and skill evolution matrices representing memory context."""
        # 1. Fetch Candidate Profile with all relations
        profile = await self.profile_repo.get_profile_with_relations(candidate_id)
        if not profile:
            raise EntityNotFoundError(f"Candidate profile '{candidate_id}' not found.")

        # 2. Fetch all Interview Sessions for candidate
        stmt_interviews = (
            select(InterviewSession)
            .where(InterviewSession.candidate_id == candidate_id)
            .order_by(InterviewSession.created_at.asc())
        )
        res_interviews = await self.db.execute(stmt_interviews)
        interviews = list(res_interviews.scalars().all())

        # 3. Fetch all Evaluation Reports for the sessions
        session_ids = [s.id for s in interviews]
        evaluations = []
        if session_ids:
            stmt_evals = (
                select(EvaluationReport)
                .where(EvaluationReport.session_id.in_(session_ids))
                .order_by(EvaluationReport.created_at.asc())
            )
            res_evals = await self.db.execute(stmt_evals)
            evaluations = list(res_evals.scalars().all())

        def _normalize_timezone(dt: datetime) -> datetime:
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)

        # 4. Build Timeline
        timeline_events = []

        # Add interview session creation & update milestones
        for session in interviews:
            timeline_events.append(
                TimelineEvent(
                    event_type="INTERVIEW",
                    title=f"Interview Session Created ({session.type})",
                    timestamp=_normalize_timezone(session.created_at),
                    details={
                        "session_id": str(session.id),
                        "type": str(session.type),
                        "status": str(session.status),
                    },
                )
            )
            # If completed or failed, add that event too
            if session.status in ("COMPLETED", "FAILED"):
                timeline_events.append(
                    TimelineEvent(
                        event_type="INTERVIEW",
                        title=f"Interview Session Ended ({session.status})",
                        timestamp=_normalize_timezone(session.updated_at),
                        details={
                            "session_id": str(session.id),
                            "type": str(session.type),
                            "status": str(session.status),
                        },
                    )
                )

        # Add evaluation reports milestones
        for report in evaluations:
            timeline_events.append(
                TimelineEvent(
                    event_type="EVALUATION",
                    title="Evaluation Report Generated",
                    timestamp=_normalize_timezone(report.created_at),
                    details={
                        "report_id": str(report.id),
                        "session_id": str(report.session_id),
                        "overall_score": report.overall_score,
                        "faithfulness_score": report.faithfulness_score,
                    },
                )
            )

        # Add interview insights milestones
        for insight in profile.insights:
            timeline_events.append(
                TimelineEvent(
                    event_type="INSIGHT",
                    title="Interview Insight Recorded",
                    timestamp=_normalize_timezone(insight.created_at),
                    details={
                        "insight_id": str(insight.id),
                        "session_id": str(insight.session_id),
                        "communication_score": insight.communication_score,
                        "confidence_score": insight.confidence_score,
                        "technical_rating": insight.technical_rating,
                    },
                )
            )

        # Add snapshots milestones
        for snapshot in profile.progress_snapshots:
            timeline_events.append(
                TimelineEvent(
                    event_type="SNAPSHOT",
                    title="Progress Snapshot Recorded",
                    timestamp=_normalize_timezone(snapshot.created_at),
                    details={
                        "snapshot_id": str(snapshot.id),
                        "overall_score": snapshot.overall_score,
                    },
                )
            )

        # Sort timeline by timestamp ascending
        timeline_events.sort(key=lambda x: x.timestamp)

        # 5. Build Skill Evolution
        skill_evolution = {}
        # Parse progress snapshots chronologically
        sorted_snapshots = sorted(
            profile.progress_snapshots, key=lambda x: _normalize_timezone(x.created_at)
        )
        for snapshot in sorted_snapshots:
            try:
                matrix = json.loads(snapshot.skills_matrix)
                for skill_name, level in matrix.items():
                    if skill_name not in skill_evolution:
                        skill_evolution[skill_name] = []
                    skill_evolution[skill_name].append(
                        {
                            "date": _normalize_timezone(
                                snapshot.created_at
                            ).isoformat(),
                            "level": level,
                        }
                    )
            except Exception:
                pass

        # 6. Build Knowledge Graph
        nodes = []
        edges = []

        # Add Candidate node
        nodes.append(
            GraphNode(
                id=str(profile.id),
                label="Candidate",
                type="CANDIDATE",
                properties={
                    "experience_years": profile.experience_years or 0.0,
                    "summary": profile.summary or "",
                },
            )
        )

        # Add Skill nodes & edges
        for cs in profile.skills:
            nodes.append(
                GraphNode(
                    id=f"skill_{cs.skill.id}",
                    label=cs.skill.name,
                    type="SKILL",
                    properties={
                        "category": cs.skill.category,
                    },
                )
            )
            edges.append(
                GraphEdge(
                    source=str(profile.id),
                    target=f"skill_{cs.skill.id}",
                    relation="POSSESSES",
                    properties={
                        "level": cs.level,
                        "confidence": cs.confidence,
                    },
                )
            )

        # Add Interview nodes & edges
        for session in interviews:
            nodes.append(
                GraphNode(
                    id=str(session.id),
                    label=f"Interview ({session.type})",
                    type="INTERVIEW",
                    properties={
                        "type": str(session.type),
                        "status": str(session.status),
                    },
                )
            )
            edges.append(
                GraphEdge(
                    source=str(profile.id),
                    target=str(session.id),
                    relation="PARTICIPATED_IN",
                    properties={},
                )
            )

        # Add Evaluation nodes & edges
        for report in evaluations:
            nodes.append(
                GraphNode(
                    id=str(report.id),
                    label=f"Evaluation ({report.overall_score})",
                    type="EVALUATION",
                    properties={
                        "overall_score": report.overall_score,
                        "faithfulness_score": report.faithfulness_score,
                    },
                )
            )
            edges.append(
                GraphEdge(
                    source=str(report.session_id),
                    target=str(report.id),
                    relation="GENERATED_EVALUATION",
                    properties={},
                )
            )

        # Add Insight nodes & edges
        for insight in profile.insights:
            nodes.append(
                GraphNode(
                    id=str(insight.id),
                    label=f"Insight ({insight.technical_rating})",
                    type="INSIGHT",
                    properties={
                        "communication_score": insight.communication_score,
                        "confidence_score": insight.confidence_score,
                    },
                )
            )
            edges.append(
                GraphEdge(
                    source=str(insight.session_id),
                    target=str(insight.id),
                    relation="PRODUCED_INSIGHT",
                    properties={},
                )
            )

        # Add Strength nodes & edges
        for st in profile.strengths:
            nodes.append(
                GraphNode(
                    id=str(st.id),
                    label=st.title,
                    type="STRENGTH",
                    properties={
                        "title": st.title,
                        "description": st.description,
                    },
                )
            )
            edges.append(
                GraphEdge(
                    source=str(profile.id),
                    target=str(st.id),
                    relation="HAS_STRENGTH",
                    properties={},
                )
            )

        # Add Weakness nodes & edges
        for w in profile.weaknesses:
            nodes.append(
                GraphNode(
                    id=str(w.id),
                    label=w.title,
                    type="WEAKNESS",
                    properties={
                        "title": w.title,
                        "description": w.description,
                    },
                )
            )
            edges.append(
                GraphEdge(
                    source=str(profile.id),
                    target=str(w.id),
                    relation="HAS_WEAKNESS",
                    properties={},
                )
            )

        # Deduplicate nodes by id
        seen_nodes = set()
        deduped_nodes = []
        for node in nodes:
            if node.id not in seen_nodes:
                seen_nodes.add(node.id)
                deduped_nodes.append(node)

        knowledge_graph = KnowledgeGraph(nodes=deduped_nodes, edges=edges)

        # Serialize evaluations using the target schema to prevent Pydantic serialization errors
        from src.contexts.evaluation.schemas import EvaluationReportResponse

        serialized_evaluations = [
            EvaluationReportResponse.model_validate(e) for e in evaluations
        ]

        return CandidateMemoryResponse(
            timeline=timeline_events,
            knowledge_graph=knowledge_graph,
            skill_evolution=skill_evolution,
            interviews=interviews,
            evaluations=serialized_evaluations,
            insights=profile.insights,
        )
