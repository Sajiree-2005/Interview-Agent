"""Candidate profile analysis and scoring."""
from typing import Dict, List, Any, Optional, Tuple
from app.models.schemas import CandidateProfile, MissionRecord
from app.core.logging import get_logger

logger = get_logger(__name__)


class CandidateAnalyzer:
    """Analyzes candidate learning history to derive signals."""

    def analyze(self, candidate: CandidateProfile) -> Dict[str, Any]:
        """Produce a comprehensive candidate analysis."""
        missions = candidate.missions
        signals = candidate.signals

        # Basic counts
        passed_days = [m.day for m in missions if m.passed]
        skipped_days = [m.day for m in missions if m.skipped]
        failed_days = [m.day for m in missions if not m.passed and not m.skipped]

        total_attempts = sum((m.attempts or 0) for m in missions)
        avg_attempts = total_attempts / len(missions) if missions else 0

        # Difficulty-weighted scores
        day_difficulty = self._estimate_day_difficulties(missions)

        # Strength/weakness signals
        strong_days = []
        weak_days = []
        for m in missions:
            if m.passed and (m.attempts or 0) <= 1:
                strong_days.append(m.day)
            elif (m.attempts or 0) >= 4 or m.skipped or (not m.passed and not m.skipped):
                weak_days.append(m.day)

        # Experience calibration
        experience_tier = self._experience_tier(candidate.member.yearsExperience)

        # First-try ratio
        first_try_ratio = signals.missionsFirstTry / signals.missionsCompleted if signals.missionsCompleted > 0 else 0

        analysis = {
            "candidate_id": candidate.member.id,
            "name": candidate.member.name,
            "role": candidate.member.jobRole,
            "years_experience": candidate.member.yearsExperience,
            "experience_tier": experience_tier,
            "education": candidate.member.education,
            "passed_days": passed_days,
            "skipped_days": skipped_days,
            "failed_days": failed_days,
            "total_missions": len(missions),
            "total_attempts": total_attempts,
            "avg_attempts": round(avg_attempts, 2),
            "strong_days": strong_days,
            "weak_days": weak_days,
            "first_try_ratio": round(first_try_ratio, 2),
            "commit_days": signals.commitDays,
            "day_difficulty": day_difficulty,
        }

        logger.info("candidate_analyzed", 
                    candidate_id=candidate.member.id,
                    strong_days=len(strong_days),
                    weak_days=len(weak_days),
                    avg_attempts=round(avg_attempts, 2))

        return analysis

    def _estimate_day_difficulties(self, missions: List[MissionRecord]) -> Dict[int, float]:
        """Estimate per-day difficulty based on attempts and pass rate."""
        difficulties = {}
        for m in missions:
            attempts = m.attempts or 1
            passed = 1.0 if m.passed else 0.0
            skipped = 1.0 if m.skipped else 0.0
            # Higher attempts = harder, skipped = very hard
            difficulties[m.day] = round(min(1.0, (attempts / 5.0) * 0.5 + skipped * 0.5 + (1 - passed) * 0.3), 2)
        return difficulties

    def _experience_tier(self, years: int) -> str:
        if years <= 1:
            return "junior"
        elif years <= 4:
            return "mid"
        elif years <= 8:
            return "senior"
        else:
            return "staff_plus"

    def get_recommended_start_difficulty(self, analysis: Dict[str, Any]) -> str:
        """Recommend initial interview difficulty based on candidate profile."""
        avg_attempts = analysis["avg_attempts"]
        first_try = analysis["first_try_ratio"]
        tier = analysis["experience_tier"]

        if tier in ("staff_plus", "senior") and first_try >= 0.7 and avg_attempts <= 1.5:
            return "advanced"
        elif tier in ("senior", "mid") and first_try >= 0.5 and avg_attempts <= 2.5:
            return "intermediate"
        elif avg_attempts > 3.5 or first_try < 0.3:
            return "foundational"
        else:
            return "intermediate"
