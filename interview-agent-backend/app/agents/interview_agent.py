"""Core interview agent orchestrating the entire interview flow."""
import json
from typing import Dict, Any, Optional
from app.models.schemas import (
    CandidateProfile, InterviewRequest, InterviewResponse
)
from app.memory.interview_memory import memory_store, InterviewState, QuestionRecord, AnswerRecord
from app.services.candidate_service import CandidateAnalyzer
from app.services.curriculum_service import curriculum_service
from app.agents.strategy_engine import strategy_engine
from app.agents.question_planner import question_planner
from app.evaluation.answer_evaluator import answer_evaluator
from app.evaluation.competency_engine import competency_engine
from app.evaluation.contradiction_detector import ContradictionDetector
from app.rag.retriever import retriever
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class InterviewAgent:
    """Orchestrates the adaptive interview process."""

    def __init__(self):
        self.analyzer = CandidateAnalyzer()
        self.settings = get_settings()

    async def handle(self, request: InterviewRequest) -> InterviewResponse:
        """Main entry point for interview requests."""
        session_id = request.sessionId

        # Check if this is a new session
        if request.candidate is not None and not memory_store.exists(session_id):
            return await self._start_interview(session_id, request.candidate)

        # Existing session - process answer
        state = memory_store.get(session_id)
        if state is None:
            logger.error("session_not_found", session_id=session_id)
            return InterviewResponse(reply="Session not found. Please start a new interview.", done=True)

        if state.interview_complete:
            return InterviewResponse(reply="Interview already completed.", done=True)

        if request.message is not None:
            return await self._process_answer(state, request.message)
        else:
            # No message - maybe asking for next question
            return await self._ask_next_question(state)

    async def _start_interview(self, session_id: str, candidate: CandidateProfile) -> InterviewResponse:
        """Initialize a new interview session."""
        # Build candidate analysis
        analysis = self.analyzer.analyze(candidate)

        # Create session
        state = memory_store.create(
            session_id=session_id,
            candidate_id=candidate.member.id,
            candidate_name=candidate.member.name,
        )

        # Generate strategy blueprint
        available_days = [d.day for d in curriculum_service.get_all_days()]
        blueprint = strategy_engine.generate_blueprint(analysis, available_days)
        state.strategy_blueprint = blueprint
        state.current_difficulty = blueprint["start_difficulty"]

        # Store analysis in state for later use
        state.candidate_analysis = analysis

        # Generate first question
        return await self._ask_next_question(state)

    async def _process_answer(self, state: InterviewState, message: str) -> InterviewResponse:
        """Process candidate answer and decide next step."""

        # Handle special responses
        message_lower = message.lower().strip()

        if message_lower in ["i don't know", "i dont know", "not sure", "no idea", "pass"]:
            return await self._handle_dont_know(state)

        # Record answer
        answer = AnswerRecord(
            question_number=state.current_question_number,
            text=message,
        )
        state.add_answer(answer)

        # Get last question
        last_qa = state.get_last_qa()
        if not last_qa:
            return await self._ask_next_question(state)

        question, _ = last_qa

        # Retrieve curriculum context for evaluation
        curriculum_context = retriever.get_context_string(question.topic, top_k=2)
        conversation_history = state.get_conversation_summary(max_turns=4)

        # Evaluate answer
        evaluation = await answer_evaluator.evaluate(
            question=question.text,
            answer=message,
            topic=question.topic,
            difficulty=question.difficulty,
            curriculum_context=curriculum_context,
            conversation_history=conversation_history,
        )

        # Update answer with evaluation
        answer.evaluation = evaluation

        # Update competencies
        competency_engine.update_from_evaluation(
            state.competencies,
            topic=question.topic,
            day=question.day,
            evaluation=evaluation,
        )

        # Check for contradictions
        detector = ContradictionDetector()
        for ans in state.answers:
            detector.add_answer(ans.question_number, question.topic, ans.text)

        contradiction = detector.detect(question.topic, message)
        if contradiction:
            state.contradictions.append(contradiction)

        # Update strengths/weaknesses
        if evaluation["overall_label"] in ("strong", "acceptable"):
            state.strengths.extend(evaluation.get("what_was_right", []))
        else:
            state.weaknesses.extend(evaluation.get("what_was_missed", []))

        if evaluation.get("misconception"):
            state.misconceptions.append(evaluation["misconception"])

        # Adapt strategy
        state.strategy_blueprint = strategy_engine.adapt_strategy(
            state.strategy_blueprint,
            state.current_question_number,
            evaluation,
            state.covered_days,
        )

        # Update difficulty
        rec = evaluation.get("next_difficulty_recommendation", "same")
        if rec == "easier":
            state.current_difficulty = self._step_down(state.current_difficulty)
        elif rec == "harder":
            state.current_difficulty = self._step_up(state.current_difficulty)

        logger.info("answer_processed",
                    session=state.session_id,
                    question=state.current_question_number,
                    label=evaluation["overall_label"],
                    difficulty=state.current_difficulty)

        # Check if interview should end
        if self._should_end(state):
            return await self._finalize_interview(state)

        # Ask next question
        return await self._ask_next_question(state)

    async def _handle_dont_know(self, state: InterviewState) -> InterviewResponse:
        """Handle candidate saying they don't know."""
        # Reduce difficulty and provide encouragement
        state.current_difficulty = self._step_down(state.current_difficulty)

        reply = "That's completely fine. Let me rephrase or move to a related but more foundational concept."

        # Still count this as an answer
        answer = AnswerRecord(
            question_number=state.current_question_number,
            text="[Candidate indicated they do not know]",
            evaluation={"overall_label": "incorrect", "next_difficulty_recommendation": "easier"},
        )
        state.add_answer(answer)

        if self._should_end(state):
            return await self._finalize_interview(state)

        next_q = await self._ask_next_question(state)
        return InterviewResponse(reply=f"{reply}\n\n{next_q.reply}", done=next_q.done)

    async def _ask_next_question(self, state: InterviewState) -> InterviewResponse:
        """Generate the next question based on strategy."""

        next_num = state.current_question_number + 1
        blueprint = state.strategy_blueprint

        # Determine target day and topic from blueprint progression
        progression = blueprint.get("progression_plan", [])
        target_day = None
        planned_difficulty = state.current_difficulty

        for item in progression:
            if item["order"] == next_num:
                target_day = item["day"]
                planned_difficulty = item.get("planned_difficulty", state.current_difficulty)
                break

        # If no planned day, pick from uncovered days
        if target_day is None:
            all_days = [d.day for d in curriculum_service.get_all_days()]
            uncovered = [d for d in all_days if d not in state.covered_days]
            if uncovered:
                target_day = uncovered[0]
            else:
                target_day = all_days[next_num % len(all_days)]

        day_data = curriculum_service.get_day(target_day)
        topic = day_data.title if day_data else "General AI Concepts"

        # Select question type
        question_type = question_planner.select_question_type(
            state.question_types_used,
            planned_difficulty,
            topic,
        )

        # Get candidate analysis
        analysis = getattr(state, 'candidate_analysis', {})
        conversation_history = state.get_conversation_summary(max_turns=3)

        # Get previous evaluation for context
        previous_eval = None
        if state.answers:
            previous_eval = state.answers[-1].evaluation

        # Generate question
        result = await question_planner.generate_question(
            day=target_day,
            topic=topic,
            difficulty=planned_difficulty,
            question_type=question_type,
            candidate_analysis=analysis,
            conversation_history=conversation_history,
            previous_eval=previous_eval,
            covered_topics=list(state.covered_topics),
        )

        question = QuestionRecord(
            question_number=next_num,
            text=result["question"],
            topic=result["topic"],
            day=result["day"],
            difficulty=result["difficulty"],
            question_type=result["question_type"],
            rationale=result.get("rationale", ""),
        )
        state.add_question(question)

        logger.info("question_asked",
                    session=state.session_id,
                    number=next_num,
                    day=target_day,
                    type=question_type,
                    difficulty=planned_difficulty)

        return InterviewResponse(reply=result["question"], done=False)

    def _should_end(self, state: InterviewState) -> bool:
        """Determine if the interview should conclude."""
        min_q = self.settings.min_questions
        max_q = self.settings.max_questions
        min_days = self.settings.min_curriculum_days

        q_count = len(state.questions)
        day_count = len(state.covered_days)

        # Must meet minimums
        if q_count < min_q or day_count < min_days:
            return False

        # Can end if we've reached max questions
        if q_count >= max_q:
            return True

        # Can end if we've covered enough and had good variety
        if q_count >= min_q and day_count >= min_days and q_count >= 8:
            return True

        return False

    async def _finalize_interview(self, state: InterviewState) -> InterviewResponse:
        """Generate final feedback and end interview."""
        state.interview_complete = True

        # Build feedback
        feedback = await self._generate_feedback(state)

        logger.info("interview_completed",
                    session=state.session_id,
                    questions=len(state.questions),
                    days=len(state.covered_days))

        return InterviewResponse(
            reply="Thank you for completing the interview. Here is your personalized feedback.",
            done=True,
            feedback=feedback,
        )

    async def _generate_feedback(self, state: InterviewState) -> Dict[str, Any]:
        """Generate structured final feedback."""

        overall = competency_engine.get_overall_scores(state.competencies)
        strengths = competency_engine.identify_strengths(state.competencies)
        gaps = competency_engine.identify_gaps(state.competencies)

        # Add conversation-derived strengths/gaps
        strengths.extend(list(set(state.strengths))[:3])
        gaps.extend(list(set(state.weaknesses))[:3])

        # Deduplicate
        strengths = list(dict.fromkeys(strengths))[:5]
        gaps = list(dict.fromkeys(gaps))[:5]

        # Generate personalized next steps
        next_steps = self._generate_learning_path(state, gaps)

        # Overall readiness score
        if overall:
            avg_score = sum(overall.values()) / len(overall)
            readiness = self._classify_readiness(avg_score)
        else:
            avg_score = 0.5
            readiness = "needs_development"

        summary = self._build_summary(state, readiness, avg_score)

        return {
            "summary": summary,
            "strengths": strengths if strengths else ["Participated actively in the interview"],
            "gaps": gaps if gaps else ["Further assessment needed across more topics"],
            "next": next_steps,
            "fingerprint": {
                "conceptual_knowledge": round(overall.get("conceptual_understanding", 0.5) * 100),
                "practical_application": round(overall.get("practical_application", 0.5) * 100),
                "engineering_reasoning": round(overall.get("engineering_reasoning", 0.5) * 100),
                "system_design": round(overall.get("system_design", 0.5) * 100),
                "communication": round(overall.get("communication", 0.5) * 100),
                "overall_readiness": round(avg_score * 100),
            },
            "coverage": {
                "questions_asked": len(state.questions),
                "days_covered": sorted(state.covered_days),
                "topics_covered": sorted(state.covered_topics),
                "question_types": dict(state.question_types_used),
            },
        }

    def _build_summary(self, state: InterviewState, readiness: str, score: float) -> str:
        name = state.candidate_name
        tier = getattr(state, 'candidate_analysis', {}).get('experience_tier', 'mid')

        readiness_text = {
            "excellent": f"{name} demonstrates strong readiness across evaluated competencies.",
            "good": f"{name} shows solid understanding with some areas for growth.",
            "developing": f"{name} has foundational knowledge but needs deeper practice.",
            "needs_development": f"{name} would benefit from focused study on core concepts.",
        }.get(readiness, f"{name} completed the interview.")

        return (
            f"{readiness_text} "
            f"Overall readiness score: {round(score * 100)}%. "
            f"Interview covered {len(state.covered_days)} curriculum days across "
            f"{len(state.covered_topics)} topics with {len(state.questions)} questions."
        )

    def _classify_readiness(self, score: float) -> str:
        if score >= 0.8:
            return "excellent"
        elif score >= 0.65:
            return "good"
        elif score >= 0.5:
            return "developing"
        else:
            return "needs_development"

    def _generate_learning_path(self, state: InterviewState, gaps: List[str]) -> List[str]:
        """Generate personalized 7-day learning path from gaps."""
        next_steps = []

        # Extract topics from gaps
        gap_topics = []
        for gap in gaps:
            # Simple extraction - look for topic names
            for day in curriculum_service.get_all_days():
                if day.title.lower() in gap.lower():
                    gap_topics.append(day)
                    break

        # Build path
        for i, day in enumerate(gap_topics[:7], 1):
            next_steps.append(f"Day {i}: Review {day.title} - focus on {'; '.join(day.objectives[:2])}")

        # Fill remaining with generic recommendations
        generic = [
            "Practice implementing core concepts in a small project",
            "Review curriculum objectives for skipped or weak days",
            "Work through debugging scenarios related to weak topics",
            "Study engineering trade-offs in production AI systems",
            "Build a end-to-end mini-project combining strong and weak areas",
        ]

        while len(next_steps) < 7:
            idx = len(next_steps) - len(gap_topics)
            if idx < len(generic):
                next_steps.append(f"Day {len(next_steps) + 1}: {generic[idx]}")
            else:
                break

        return next_steps[:7]

    def _step_up(self, diff: str) -> str:
        levels = ["foundational", "intermediate", "advanced", "expert"]
        idx = levels.index(diff) if diff in levels else 1
        return levels[min(3, idx + 1)]

    def _step_down(self, diff: str) -> str:
        levels = ["foundational", "intermediate", "advanced", "expert"]
        idx = levels.index(diff) if diff in levels else 1
        return levels[max(0, idx - 1)]


# Singleton
interview_agent = InterviewAgent()
