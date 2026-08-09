"""Question generation and grounding validation."""
import json
import re
from typing import Dict, Any, List, Optional
from app.models.schemas import QuestionType, DifficultyLevel
from app.rag.retriever import retriever
from app.services.curriculum_service import curriculum_service
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class QuestionPlanner:
    """Generates curriculum-grounded interview questions."""

    def __init__(self):
        self._client = None
        self._question_templates = self._load_templates()

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            settings = get_settings()
            self._client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )
        return self._client

    def _load_templates(self) -> Dict[str, List[str]]:
        """Pre-defined question templates per type for fallback."""
        return {
            "definition": [
                "Can you explain what {topic} is and why it matters?",
                "How would you define {topic} to a colleague?",
            ],
            "conceptual": [
                "What are the core principles behind {topic}?",
                "How does {topic} work under the hood?",
            ],
            "application": [
                "Walk me through how you would implement {topic} in a project.",
                "Describe a practical use case where {topic} is essential.",
            ],
            "scenario": [
                "Imagine your {topic} system is experiencing {problem}. How would you investigate?",
                "You need to build a solution using {topic} with {constraint}. What's your approach?",
            ],
            "debugging": [
                "Your team reports that {topic} is producing unexpected results. How do you debug it?",
                "You notice {symptom} in your {topic} pipeline. What could be wrong?",
            ],
            "trade_off": [
                "When choosing between {option_a} and {option_b} for {topic}, what factors matter most?",
                "What are the main trade-offs when scaling {topic} in production?",
            ],
            "architecture": [
                "Design a production-ready architecture for {topic}.",
                "How would you architect a system centered around {topic}?",
            ],
            "system_design": [
                "Design an end-to-end system that leverages {topic} for a healthcare chatbot.",
                "How would you integrate {topic} into a multi-component AI pipeline?",
            ],
        }

    async def generate_question(
        self,
        day: int,
        topic: str,
        difficulty: str,
        question_type: str,
        candidate_analysis: Dict[str, Any],
        conversation_history: str,
        previous_eval: Optional[Dict[str, Any]],
        covered_topics: List[str],
    ) -> Dict[str, Any]:
        """Generate a curriculum-grounded question."""

        # Retrieve curriculum context
        curriculum_context = retriever.get_context_string(topic, top_k=2)
        day_data = curriculum_service.get_day(day)

        if not day_data:
            return self._fallback_question(day, topic, difficulty, question_type)

        # Build prompt
        candidate_context = f"""
Candidate: {candidate_analysis.get('name', 'Unknown')} ({candidate_analysis.get('role', 'Unknown')}, {candidate_analysis.get('years_experience', 0)}y exp)
Experience tier: {candidate_analysis.get('experience_tier', 'mid')}
Strong days: {candidate_analysis.get('strong_days', [])}
Weak days: {candidate_analysis.get('weak_days', [])}
"""

        previous_context = ""
        if previous_eval:
            previous_context = f"""
Previous answer evaluation:
- Label: {previous_eval.get('overall_label', 'partial')}
- What was right: {previous_eval.get('what_was_right', [])}
- What was missed: {previous_eval.get('what_was_missed', [])}
- Recommendation: {previous_eval.get('next_difficulty_recommendation', 'same')}
"""

        prompt = f"""You are an expert technical interviewer. Generate ONE interview question.

## Curriculum Context
{curriculum_context}

## Target Day
Day {day}: {day_data.title}
Tools: {', '.join(day_data.tools)}
Objectives: {'; '.join(day_data.objectives[:3])}

## Candidate Profile
{candidate_context}

## Conversation History
{conversation_history}

{previous_context}

## Question Requirements
- Difficulty: {difficulty}
- Question type: {question_type}
- Must be grounded in the curriculum day above
- Must test real understanding, not just memorization
- Prefer scenario-based and trade-off questions for intermediate+
- For weak candidates, use foundational conceptual questions
- For strong candidates, ask about architecture and production concerns
- Do NOT repeat topics already covered: {covered_topics}

Respond ONLY as valid JSON:
{{
  "question": "the exact question text",
  "topic": "{topic}",
  "day": {day},
  "difficulty": "{difficulty}",
  "question_type": "{question_type}",
  "rationale": "why this question was chosen",
  "expected_concepts": ["concept1", "concept2"]
}}
"""

        try:
            client = self._get_client()
            response = await client.chat.completions.create(
                model=get_settings().openai_model,
                messages=[
                    {"role": "system", "content": "You generate precise technical interview questions. Output only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=400,
            )
            content = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            result = json.loads(content)

            # Validate grounding
            validated = self._validate_question(result, day_data)
            if not validated["valid"]:
                logger.warning("question_validation_failed", reason=validated["reason"])
                return self._fallback_question(day, topic, difficulty, question_type)

            logger.info("question_generated", day=day, type=question_type, difficulty=difficulty)
            return result

        except Exception as e:
            logger.error("question_generation_failed", error=str(e))
            return self._fallback_question(day, topic, difficulty, question_type)

    def _validate_question(self, result: Dict[str, Any], day_data) -> Dict[str, Any]:
        """Validate that a generated question is properly grounded."""
        question = result.get("question", "")

        # Check curriculum grounding
        title_words = set(day_data.title.lower().split())
        tool_words = set(t.lower() for t in day_data.tools)
        question_words = set(question.lower().split())

        has_topic_overlap = bool((title_words | tool_words) & question_words)

        if not has_topic_overlap:
            return {"valid": False, "reason": "question not grounded in curriculum topic"}

        if len(question) < 20:
            return {"valid": False, "reason": "question too short"}

        return {"valid": True, "reason": ""}

    def _fallback_question(self, day: int, topic: str, difficulty: str, question_type: str) -> Dict[str, Any]:
        """Generate a fallback question from templates."""
        templates = self._question_templates.get(question_type, self._question_templates["conceptual"])
        import random
        template = random.choice(templates)

        # Fill in template
        day_data = curriculum_service.get_day(day)
        tools = day_data.tools if day_data else [topic]

        question = template.format(
            topic=topic,
            problem="performance issues",
            constraint="limited budget",
            option_a=tools[0] if tools else "approach A",
            option_b=tools[1] if len(tools) > 1 else "approach B",
            symptom="unexpected output",
        )

        return {
            "question": question,
            "topic": topic,
            "day": day,
            "difficulty": difficulty,
            "question_type": question_type,
            "rationale": f"Fallback question for {topic} at {difficulty} level",
            "expected_concepts": [topic],
        }

    def select_question_type(self, used_types: Dict[str, int], difficulty: str, topic: str) -> str:
        """Select a diverse question type based on history and difficulty."""
        import random

        # Type pools by difficulty
        type_pools = {
            "foundational": ["definition", "conceptual", "application"],
            "intermediate": ["conceptual", "application", "scenario", "debugging"],
            "advanced": ["scenario", "trade_off", "architecture", "debugging"],
            "expert": ["trade_off", "architecture", "system_design"],
        }

        pool = type_pools.get(difficulty, type_pools["intermediate"])

        # Prefer less-used types
        type_scores = {}
        for qt in pool:
            count = used_types.get(qt, 0)
            type_scores[qt] = 1.0 / (1 + count)

        # Weighted random selection
        total = sum(type_scores.values())
        r = random.uniform(0, total)
        cumulative = 0
        for qt, score in type_scores.items():
            cumulative += score
            if r <= cumulative:
                return qt

        return pool[0]


# Singleton
question_planner = QuestionPlanner()
