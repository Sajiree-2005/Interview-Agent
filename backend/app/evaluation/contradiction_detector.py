"""Lightweight semantic contradiction detection."""
import re
from typing import List, Dict, Any, Optional
from app.core.logging import get_logger

logger = get_logger(__name__)


class ContradictionDetector:
    """Detects meaningful technical contradictions in candidate answers."""

    # Topic-specific contradiction patterns
    CONTRADICTION_PATTERNS = {
        "rag": [
            ("rag is necessary because model cannot access private docs", 
             "model already knows all private documents", 
             "RAG vs memorization"),
            ("use rag for everything", 
             "rag is always worse than fine-tuning", 
             "RAG vs fine-tuning stance"),
        ],
        "vector_db": [
            ("faiss is better for all cases", 
             "managed vector db is always better", 
             "FAISS vs managed DB stance"),
        ],
        "fine_tuning": [
            ("fine-tuning replaces rag", 
             "rag replaces fine-tuning", 
             "RAG vs fine-tuning relationship"),
        ],
        "deployment": [
            ("docker is enough for production", 
             "kubernetes is overkill", 
             "Deployment complexity view"),
        ],
    }

    def __init__(self):
        self._history: List[Dict[str, Any]] = []

    def add_answer(self, question_number: int, topic: str, answer: str) -> None:
        self._history.append({
            "question_number": question_number,
            "topic": topic.lower(),
            "answer": answer.lower(),
        })

    def detect(self, current_topic: str, current_answer: str) -> Optional[Dict[str, Any]]:
        """Check if current answer contradicts any previous answer."""
        current_lower = current_answer.lower()
        topic_lower = current_topic.lower()

        # Find relevant patterns for this topic
        patterns = []
        for key, pats in self.CONTRADICTION_PATTERNS.items():
            if key in topic_lower or topic_lower in key:
                patterns.extend(pats)

        # Also check general patterns
        for prev in self._history:
            # Skip if same question
            if prev["topic"] != topic_lower:
                continue

            for pat_a, pat_b, description in patterns:
                a_in_prev = pat_a in prev["answer"]
                b_in_current = pat_b in current_lower
                b_in_prev = pat_b in prev["answer"]
                a_in_current = pat_a in current_lower

                if (a_in_prev and b_in_current) or (b_in_prev and a_in_current):
                    logger.info("contradiction_detected", 
                                topic=topic_lower,
                                description=description,
                                prev_q=prev["question_number"])
                    return {
                        "detected": True,
                        "description": description,
                        "previous_question": prev["question_number"],
                        "severity": "medium",
                    }

        # Semantic similarity check for key claims
        return self._semantic_check(current_topic, current_answer)

    def _semantic_check(self, topic: str, answer: str) -> Optional[Dict[str, Any]]:
        """Additional semantic consistency checks."""
        # Check for direct negation of previous claims
        negation_markers = ["not", "never", "no longer", "actually", "contrary"]
        answer_lower = answer.lower()

        for prev in self._history:
            if prev["topic"] != topic.lower():
                continue
            for marker in negation_markers:
                if marker in answer_lower:
                    # Simple check: if previous had a strong claim and current negates
                    strong_claims = ["always", "definitely", "must", "only", "best"]
                    for claim in strong_claims:
                        if claim in prev["answer"] and marker in answer_lower:
                            # Potential contradiction - but be conservative
                            return {
                                "detected": True,
                                "description": f"Possible reversal of previous stance on {topic}",
                                "previous_question": prev["question_number"],
                                "severity": "low",
                            }
        return None


# Singleton
contradiction_detector = ContradictionDetector()
