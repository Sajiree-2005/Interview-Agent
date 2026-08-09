"""Tests for evaluation and strategy components."""
import pytest
from app.services.candidate_service import CandidateAnalyzer
from app.agents.strategy_engine import StrategyEngine
from app.evaluation.competency_engine import CompetencyEngine
from app.models.schemas import CandidateProfile, MemberProfile, LearningSignals, MissionRecord


def make_candidate(attempts_map):
    missions = []
    for day, attempts in attempts_map.items():
        missions.append(MissionRecord(day=day, title=f"Day {day}", passed=True, attempts=attempts))
    return CandidateProfile(
        member=MemberProfile(id="C1", name="Test", jobRole="Engineer", yearsExperience=5, education="BS", status="DONE"),
        missions=missions,
        signals=LearningSignals(commitDays=20, missionsCompleted=10, missionsFirstTry=5)
    )


class TestCandidateAnalyzer:
    def test_strong_candidate(self):
        analyzer = CandidateAnalyzer()
        c = make_candidate({7: 1, 8: 1, 10: 1, 12: 1})
        analysis = analyzer.analyze(c)
        assert analysis["avg_attempts"] == 1.0
        assert len(analysis["strong_days"]) == 4

    def test_weak_candidate(self):
        analyzer = CandidateAnalyzer()
        c = make_candidate({7: 5, 8: 4, 10: 5, 12: 3})
        analysis = analyzer.analyze(c)
        assert analysis["avg_attempts"] > 3.0
        assert len(analysis["weak_days"]) >= 3


class TestStrategyEngine:
    def test_blueprint_generation(self):
        engine = StrategyEngine()
        analysis = {
            "candidate_id": "C1",
            "name": "Test",
            "role": "Engineer",
            "years_experience": 5,
            "experience_tier": "mid",
            "strong_days": [7, 8],
            "weak_days": [22, 23],
            "passed_days": [7, 8, 10, 12, 22, 23],
            "skipped_days": [],
            "failed_days": [],
            "avg_attempts": 2.0,
            "first_try_ratio": 0.5,
        }
        blueprint = engine.generate_blueprint(analysis, list(range(1, 32)))
        assert "topics_to_test" in blueprint
        assert "progression_plan" in blueprint
        assert len(blueprint["progression_plan"]) > 0


class TestCompetencyEngine:
    def test_update_and_aggregate(self):
        engine = CompetencyEngine()
        comps = {}
        engine.update_from_evaluation(comps, "Vector DBs", 8, {
            "conceptual_depth": 0.8,
            "practical_understanding": 0.6,
            "engineering_reasoning": 0.5,
            "communication_clarity": 0.7,
            "correctness": 0.75,
            "what_was_right": ["Good explanation"],
            "what_was_missed": [],
        })
        assert "8:Vector DBs" in comps
        overall = engine.get_overall_scores(comps)
        assert overall["conceptual_understanding"] > 0
