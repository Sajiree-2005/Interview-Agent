"""Interview strategy engine - builds and adapts interview blueprints."""
from typing import Dict, Any, List, Set, Optional
from app.models.schemas import DifficultyLevel, QuestionType
from app.services.candidate_service import CandidateAnalyzer
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class StrategyEngine:
    """Generates and updates interview strategy based on candidate profile and performance."""

    def __init__(self):
        self.analyzer = CandidateAnalyzer()

    def generate_blueprint(
        self,
        candidate_analysis: Dict[str, Any],
        available_days: List[int],
    ) -> Dict[str, Any]:
        """Generate initial interview blueprint from candidate analysis."""

        strong_days = set(candidate_analysis.get("strong_days", []))
        weak_days = set(candidate_analysis.get("weak_days", []))
        passed_days = set(candidate_analysis.get("passed_days", []))
        skipped_days = set(candidate_analysis.get("skipped_days", []))
        failed_days = set(candidate_analysis.get("failed_days", []))

        # Determine topics to test
        topics_to_test = []
        topics_to_probe = []
        topics_to_avoid = []

        # Priority 1: Weak/skip days (need assessment)
        for day in weak_days:
            if day in available_days:
                topics_to_test.append({
                    "day": day,
                    "priority": "high",
                    "reason": "candidate showed struggle or skipped this topic",
                    "suggested_difficulty": "foundational",
                    "suggested_types": ["definition", "conceptual"],
                })

        # Priority 2: Strong days (verify depth)
        for day in strong_days:
            if day in available_days and day not in [t["day"] for t in topics_to_test]:
                topics_to_probe.append({
                    "day": day,
                    "priority": "medium",
                    "reason": "candidate passed easily - verify deep understanding",
                    "suggested_difficulty": "intermediate",
                    "suggested_types": ["scenario", "trade_off", "application"],
                })

        # Priority 3: Other passed days (spot check)
        other_passed = passed_days - strong_days - weak_days
        for day in other_passed:
            if day in available_days and day not in [t["day"] for t in topics_to_test + topics_to_probe]:
                topics_to_test.append({
                    "day": day,
                    "priority": "low",
                    "reason": "covered topic - verify retention",
                    "suggested_difficulty": "intermediate",
                    "suggested_types": ["conceptual", "application"],
                })

        # Priority 4: Failed days
        for day in failed_days:
            if day in available_days:
                topics_to_test.append({
                    "day": day,
                    "priority": "high",
                    "reason": "candidate failed this mission",
                    "suggested_difficulty": "foundational",
                    "suggested_types": ["definition", "conceptual"],
                })

        # Determine starting difficulty
        start_difficulty = self.analyzer.get_recommended_start_difficulty(candidate_analysis)

        # Build progression plan
        progression = self._build_progression(topics_to_test + topics_to_probe, start_difficulty)

        blueprint = {
            "candidate_id": candidate_analysis["candidate_id"],
            "experience_tier": candidate_analysis["experience_tier"],
            "start_difficulty": start_difficulty,
            "topics_to_test": topics_to_test,
            "topics_to_probe": topics_to_probe,
            "topics_to_avoid": topics_to_avoid,
            "progression_plan": progression,
            "coverage_target": {
                "min_questions": get_settings().min_questions,
                "max_questions": get_settings().max_questions,
                "min_days": get_settings().min_curriculum_days,
            },
            "strategy_notes": self._generate_strategy_notes(candidate_analysis),
        }

        logger.info("blueprint_generated", 
                    candidate=candidate_analysis["candidate_id"],
                    topics=len(topics_to_test) + len(topics_to_probe),
                    start_difficulty=start_difficulty)

        return blueprint

    def _build_progression(self, topics: List[Dict[str, Any]], start_difficulty: str) -> List[Dict[str, Any]]:
        """Build an ordered progression of topics for the interview."""
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sorted_topics = sorted(topics, key=lambda x: priority_order.get(x["priority"], 3))

        progression = []
        for i, topic in enumerate(sorted_topics[:get_settings().max_questions]):
            diff = self._progress_difficulty(start_difficulty, i)
            progression.append({
                "order": i + 1,
                "day": topic["day"],
                "priority": topic["priority"],
                "planned_difficulty": diff,
                "planned_types": topic["suggested_types"],
            })

        return progression

    def _progress_difficulty(self, start: str, question_index: int) -> str:
        """Gradually increase difficulty based on position."""
        levels = ["foundational", "intermediate", "advanced", "expert"]
        start_idx = levels.index(start) if start in levels else 1
        # Increase every 2-3 questions
        increment = question_index // 3
        new_idx = min(len(levels) - 1, start_idx + increment)
        return levels[new_idx]

    def _generate_strategy_notes(self, analysis: Dict[str, Any]) -> List[str]:
        notes = []
        if analysis.get("avg_attempts", 0) > 3.5:
            notes.append("Candidate struggles with missions - use scaffolding and foundational questions")
        if analysis.get("first_try_ratio", 0) > 0.8:
            notes.append("Strong first-try rate - candidate learns quickly, can accelerate")
        if analysis["experience_tier"] in ("senior", "staff_plus"):
            notes.append("Senior candidate - emphasize system design and architecture questions")
        if analysis["experience_tier"] == "junior":
            notes.append("Junior candidate - focus on fundamentals and practical application")
        if len(analysis.get("skipped_days", [])) > 2:
            notes.append("Multiple skipped topics - verify if gaps are genuine or time constraints")
        return notes

    def adapt_strategy(
        self,
        blueprint: Dict[str, Any],
        current_question: int,
        last_evaluation: Optional[Dict[str, Any]],
        covered_days: Set[int],
    ) -> Dict[str, Any]:
        """Adapt strategy based on latest evaluation."""

        if last_evaluation is None:
            return blueprint

        label = last_evaluation.get("overall_label", "partial")
        rec = last_evaluation.get("next_difficulty_recommendation", "same")

        # Update next planned difficulty
        for item in blueprint.get("progression_plan", []):
            if item["order"] == current_question + 1:
                if rec == "easier":
                    item["planned_difficulty"] = self._step_down(item["planned_difficulty"])
                elif rec == "harder":
                    item["planned_difficulty"] = self._step_up(item["planned_difficulty"])
                elif rec == "deeper":
                    item["planned_types"] = ["scenario", "trade_off", "architecture"]

        # Add adaptation note
        blueprint.setdefault("adaptations", []).append({
            "after_question": current_question,
            "evaluation_label": label,
            "difficulty_adjustment": rec,
        })

        return blueprint

    def _step_up(self, diff: str) -> str:
        levels = ["foundational", "intermediate", "advanced", "expert"]
        idx = levels.index(diff) if diff in levels else 1
        return levels[min(len(levels) - 1, idx + 1)]

    def _step_down(self, diff: str) -> str:
        levels = ["foundational", "intermediate", "advanced", "expert"]
        idx = levels.index(diff) if diff in levels else 1
        return levels[max(0, idx - 1)]


# Singleton
strategy_engine = StrategyEngine()
