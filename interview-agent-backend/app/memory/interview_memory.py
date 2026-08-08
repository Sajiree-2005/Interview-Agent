"""Interview memory and state management."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from app.models.schemas import (
    TopicCompetency, CompetencyDimension, EvaluationLabel, 
    QuestionType, DifficultyLevel
)
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class QuestionRecord:
    question_number: int
    text: str
    topic: str
    day: int
    difficulty: str
    question_type: str
    rationale: str = ""


@dataclass
class AnswerRecord:
    question_number: int
    text: str
    evaluation: Optional[Dict[str, Any]] = None


@dataclass
class InterviewState:
    session_id: str
    candidate_id: str
    candidate_name: str
    current_question_number: int = 0
    questions: List[QuestionRecord] = field(default_factory=list)
    answers: List[AnswerRecord] = field(default_factory=list)
    competencies: Dict[str, TopicCompetency] = field(default_factory=dict)
    covered_days: set = field(default_factory=set)
    covered_topics: set = field(default_factory=set)
    question_types_used: Dict[str, int] = field(default_factory=dict)
    contradictions: List[Dict[str, Any]] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    misconceptions: List[str] = field(default_factory=list)
    current_difficulty: str = "intermediate"
    interview_complete: bool = False
    strategy_blueprint: Optional[Dict[str, Any]] = None

    def add_question(self, q: QuestionRecord) -> None:
        self.questions.append(q)
        self.covered_topics.add(q.topic)
        self.covered_days.add(q.day)
        self.question_types_used[q.question_type] = self.question_types_used.get(q.question_type, 0) + 1
        self.current_question_number = q.question_number

    def add_answer(self, a: AnswerRecord) -> None:
        self.answers.append(a)

    def get_last_qa(self) -> Optional[tuple]:
        if not self.questions or not self.answers:
            return None
        return (self.questions[-1], self.answers[-1])

    def get_conversation_summary(self, max_turns: int = 6) -> str:
        """Get recent conversation history as text."""
        lines = []
        recent_q = self.questions[-max_turns:]
        recent_a = {a.question_number: a for a in self.answers[-max_turns:]}
        for q in recent_q:
            lines.append(f"Q{q.question_number} [{q.difficulty}] ({q.topic}): {q.text}")
            if q.question_number in recent_a:
                ans = recent_a[q.question_number]
                lines.append(f"A{q.question_number}: {ans.text[:300]}")
        return "\n".join(lines)

    def get_competency_summary(self) -> str:
        """Get competency scores as readable text."""
        lines = []
        for topic, comp in self.competencies.items():
            d = comp.dimensions
            lines.append(
                f"{topic}: conceptual={d.conceptual_understanding:.2f}, "
                f"practical={d.practical_application:.2f}, "
                f"reasoning={d.engineering_reasoning:.2f}, "
                f"communication={d.communication:.2f}"
            )
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "candidate_id": self.candidate_id,
            "current_question_number": self.current_question_number,
            "covered_days": sorted(self.covered_days),
            "covered_topics": sorted(self.covered_topics),
            "question_types_used": self.question_types_used,
            "current_difficulty": self.current_difficulty,
            "interview_complete": self.interview_complete,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "misconceptions": self.misconceptions,
        }


class MemoryStore:
    """In-memory session store for interview states."""

    def __init__(self):
        self._sessions: Dict[str, InterviewState] = {}

    def create(self, session_id: str, candidate_id: str, candidate_name: str) -> InterviewState:
        state = InterviewState(
            session_id=session_id,
            candidate_id=candidate_id,
            candidate_name=candidate_name,
        )
        self._sessions[session_id] = state
        logger.info("session_created", session_id=session_id, candidate_id=candidate_id)
        return state

    def get(self, session_id: str) -> Optional[InterviewState]:
        return self._sessions.get(session_id)

    def exists(self, session_id: str) -> bool:
        return session_id in self._sessions

    def delete(self, session_id: str) -> None:
        if session_id in self._sessions:
            del self._sessions[session_id]


# Singleton
memory_store = MemoryStore()
