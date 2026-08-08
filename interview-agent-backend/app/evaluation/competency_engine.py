"""Evidence-based competency tracking and scoring."""
from typing import Dict, Any, List
from app.models.schemas import TopicCompetency, CompetencyDimension
from app.core.logging import get_logger

logger = get_logger(__name__)


class CompetencyEngine:
    """Maintains and updates candidate competency scores with evidence."""

    def update_from_evaluation(
        self,
        competencies: Dict[str, TopicCompetency],
        topic: str,
        day: int,
        evaluation: Dict[str, Any],
    ) -> TopicCompetency:
        """Update competency scores based on a new evaluation."""

        key = f"{day}:{topic}"
        if key not in competencies:
            competencies[key] = TopicCompetency(topic=topic, day=day)

        comp = competencies[key]

        # Weighted update (exponential moving average)
        alpha = 0.4  # learning rate for new evidence

        dims = comp.dimensions
        dims.conceptual_understanding = self._ema(
            dims.conceptual_understanding, evaluation.get("conceptual_depth", 0.5), alpha
        )
        dims.practical_application = self._ema(
            dims.practical_application, evaluation.get("practical_understanding", 0.5), alpha
        )
        dims.engineering_reasoning = self._ema(
            dims.engineering_reasoning, evaluation.get("engineering_reasoning", 0.5), alpha
        )
        dims.system_design = self._ema(
            dims.system_design, evaluation.get("trade_off_awareness", 0.5), alpha
        )
        dims.communication = self._ema(
            dims.communication, evaluation.get("communication_clarity", 0.5), alpha
        )
        dims.confidence = self._ema(
            dims.confidence, evaluation.get("correctness", 0.5), alpha
        )

        # Add evidence
        comp.evidence.extend(evaluation.get("what_was_right", []))
        comp.evidence.extend(evaluation.get("what_was_missed", []))
        comp.evidence = comp.evidence[-10:]  # keep last 10

        # Update assessment confidence (more evidence = more confident)
        comp.confidence_in_assessment = min(0.95, 0.3 + len(comp.evidence) * 0.08)

        logger.info("competency_updated", topic=topic, day=day, 
                    conceptual=round(dims.conceptual_understanding, 2))
        return comp

    def _ema(self, old: float, new: float, alpha: float) -> float:
        return round(old * (1 - alpha) + new * alpha, 2)

    def get_overall_scores(self, competencies: Dict[str, TopicCompetency]) -> Dict[str, float]:
        """Aggregate competency scores across all topics."""
        if not competencies:
            return {}

        totals = {
            "conceptual_understanding": 0.0,
            "practical_application": 0.0,
            "engineering_reasoning": 0.0,
            "system_design": 0.0,
            "communication": 0.0,
            "confidence": 0.0,
        }

        for comp in competencies.values():
            d = comp.dimensions
            totals["conceptual_understanding"] += d.conceptual_understanding
            totals["practical_application"] += d.practical_application
            totals["engineering_reasoning"] += d.engineering_reasoning
            totals["system_design"] += d.system_design
            totals["communication"] += d.communication
            totals["confidence"] += d.confidence

        n = len(competencies)
        return {k: round(v / n, 2) for k, v in totals.items()}

    def identify_strengths(self, competencies: Dict[str, TopicCompetency]) -> List[str]:
        strengths = []
        for comp in competencies.values():
            d = comp.dimensions
            avg = (d.conceptual_understanding + d.practical_application + 
                   d.engineering_reasoning + d.communication) / 4
            if avg >= 0.75:
                strengths.append(f"{comp.topic}: strong overall understanding (avg {avg:.0%})")
            elif d.communication >= 0.8:
                strengths.append(f"{comp.topic}: excellent communication of technical concepts")
            elif d.conceptual_understanding >= 0.8:
                strengths.append(f"{comp.topic}: deep conceptual knowledge")
        return strengths

    def identify_gaps(self, competencies: Dict[str, TopicCompetency]) -> List[str]:
        gaps = []
        for comp in competencies.values():
            d = comp.dimensions
            avg = (d.conceptual_understanding + d.practical_application + 
                   d.engineering_reasoning) / 3
            if avg < 0.5:
                gaps.append(f"{comp.topic}: foundational understanding needs work (avg {avg:.0%})")
            elif d.practical_application < 0.5 and d.conceptual_understanding > 0.6:
                gaps.append(f"{comp.topic}: strong theory but weak practical application")
            elif d.engineering_reasoning < 0.5:
                gaps.append(f"{comp.topic}: needs more practice with engineering trade-offs")
        return gaps


# Singleton
competency_engine = CompetencyEngine()
