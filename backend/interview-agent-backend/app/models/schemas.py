"""Pydantic schemas for the Interview Agent API."""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum


class DifficultyLevel(str, Enum):
    FOUNDATIONAL = "foundational"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class QuestionType(str, Enum):
    DEFINITION = "definition"
    CONCEPTUAL = "conceptual"
    APPLICATION = "application"
    SCENARIO = "scenario"
    DEBUGGING = "debugging"
    TRADE_OFF = "trade_off"
    ARCHITECTURE = "architecture"
    SYSTEM_DESIGN = "system_design"


class EvaluationLabel(str, Enum):
    STRONG = "strong"
    ACCEPTABLE = "acceptable"
    PARTIAL = "partial"
    WEAK = "weak"
    INCORRECT = "incorrect"


class MissionRecord(BaseModel):
    day: int
    title: str
    passed: Optional[bool] = None
    attempts: Optional[int] = None
    skipped: Optional[bool] = None


class MemberProfile(BaseModel):
    id: str
    name: str
    jobRole: str
    yearsExperience: int
    education: str
    status: str


class LearningSignals(BaseModel):
    commitDays: int
    missionsCompleted: int
    missionsFirstTry: int


class CandidateProfile(BaseModel):
    member: MemberProfile
    missions: List[MissionRecord]
    signals: LearningSignals


class CompetencyDimension(BaseModel):
    conceptual_understanding: float = Field(0.0, ge=0.0, le=1.0)
    practical_application: float = Field(0.0, ge=0.0, le=1.0)
    engineering_reasoning: float = Field(0.0, ge=0.0, le=1.0)
    system_design: float = Field(0.0, ge=0.0, le=1.0)
    communication: float = Field(0.0, ge=0.0, le=1.0)
    confidence: float = Field(0.0, ge=0.0, le=1.0)


class TopicCompetency(BaseModel):
    topic: str
    day: int
    dimensions: CompetencyDimension
    evidence: List[str] = Field(default_factory=list)
    confidence_in_assessment: float = Field(0.5, ge=0.0, le=1.0)


class InterviewRequest(BaseModel):
    sessionId: str
    candidate: Optional[CandidateProfile] = None
    message: Optional[str] = None


class InterviewResponse(BaseModel):
    reply: str
    done: bool = False
    feedback: Optional[Dict[str, Any]] = None


class FeedbackData(BaseModel):
    summary: str
    strengths: List[str]
    gaps: List[str]
    next: List[str]


class CurriculumDay(BaseModel):
    day: int
    title: str
    type: str
    tools: List[str]
    objectives: List[str]


class CurriculumModule(BaseModel):
    n: int
    title: str
    days: List[int]


class CurriculumData(BaseModel):
    cohort: str
    modules: List[CurriculumModule]
    days: List[CurriculumDay]
