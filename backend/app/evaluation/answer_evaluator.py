"""Answer evaluation using structured LLM-based assessment."""
import json
import re
from typing import Dict, Any, Optional
from app.models.schemas import EvaluationLabel
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AnswerEvaluator:
    """Evaluates candidate answers with multi-dimensional scoring."""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            settings = get_settings()
            self._client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )
        return self._client

    async def evaluate(
        self,
        question: str,
        answer: str,
        topic: str,
        difficulty: str,
        curriculum_context: str,
        conversation_history: str,
    ) -> Dict[str, Any]:
        """Evaluate a candidate answer and return structured scores."""

        if not answer or not answer.strip():
            return self._empty_evaluation()

        settings = get_settings()

        prompt = f"""You are a senior technical interviewer evaluating a candidate's answer.

## Curriculum Context
{curriculum_context}

## Conversation History
{conversation_history}

## Current Question
Topic: {topic}
Difficulty: {difficulty}
Question: {question}

## Candidate Answer
{answer}

## Evaluation Instructions
Evaluate the answer across these dimensions (0.0 to 1.0):
- correctness: Is the technical content accurate?
- conceptual_depth: Does the answer show deep understanding or just surface knowledge?
- practical_understanding: Can the candidate apply this in practice?
- engineering_reasoning: Does the candidate reason about trade-offs and decisions?
- trade_off_awareness: Does the candidate consider alternatives and their pros/cons?
- communication_clarity: Is the answer clear, structured, and well-communicated?

Also provide:
- overall_label: one of [strong, acceptable, partial, weak, incorrect]
- what_was_right: list of what the candidate got right
- what_was_missed: list of what they missed or got wrong
- misconception: any misconception detected (or null)
- probe_suggestion: what follow-up would best test their depth
- next_difficulty_recommendation: [easier, same, deeper, harder]

Respond ONLY as valid JSON with this exact structure:
{{
  "correctness": 0.0,
  "conceptual_depth": 0.0,
  "practical_understanding": 0.0,
  "engineering_reasoning": 0.0,
  "trade_off_awareness": 0.0,
  "communication_clarity": 0.0,
  "overall_label": "",
  "what_was_right": [],
  "what_was_missed": [],
  "misconception": null,
  "probe_suggestion": "",
  "next_difficulty_recommendation": ""
}}
"""

        try:
            client = self._get_client()
            response = await client.chat.completions.create(
                model=settings.eval_model,
                messages=[
                    {"role": "system", "content": "You are a precise technical evaluator. Output only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=800,
            )
            content = response.choices[0].message.content
            # Extract JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            result = json.loads(content)

            # Normalize
            result["overall_label"] = result.get("overall_label", "partial").lower().strip()
            result["next_difficulty_recommendation"] = result.get("next_difficulty_recommendation", "same").lower().strip()

            logger.info("answer_evaluated", 
                        overall=result["overall_label"],
                        correctness=result.get("correctness", 0))
            return result

        except Exception as e:
            err_str = str(e).lower()
            if "429" in err_str or "quota" in err_str or "credit" in err_str or "insufficient" in err_str:
                logger.error("openai_quota_exhausted", error=str(e))
            else:
                logger.error("evaluation_failed", error=str(e))
            return self._fallback_evaluation(answer)

    def _empty_evaluation(self) -> Dict[str, Any]:
        return {
            "correctness": 0.0,
            "conceptual_depth": 0.0,
            "practical_understanding": 0.0,
            "engineering_reasoning": 0.0,
            "trade_off_awareness": 0.0,
            "communication_clarity": 0.0,
            "overall_label": "incorrect",
            "what_was_right": [],
            "what_was_missed": ["No answer provided"],
            "misconception": None,
            "probe_suggestion": "Ask the candidate to share their understanding of the topic.",
            "next_difficulty_recommendation": "easier",
        }

    def _fallback_evaluation(self, answer: str) -> Dict[str, Any]:
        """Heuristic fallback when LLM fails."""
        length = len(answer.split())
        has_technical = any(kw in answer.lower() for kw in [
            "because", "trade-off", "however", "architecture", "performance",
            "latency", "cost", "scalability", "security", "optimization",
            "vector", "embedding", "retrieval", "prompt", "agent", "rag"
        ])
        
        base = 0.3 if length > 10 else 0.1
        base += 0.2 if has_technical else 0.0
        base += min(0.3, length / 100)
        
        label = "acceptable" if base > 0.6 else ("partial" if base > 0.4 else "weak")
        
        return {
            "correctness": round(base, 2),
            "conceptual_depth": round(base * 0.8, 2),
            "practical_understanding": round(base * 0.7, 2),
            "engineering_reasoning": round(base * 0.6, 2),
            "trade_off_awareness": round(base * 0.5, 2),
            "communication_clarity": round(min(1.0, length / 50), 2),
            "overall_label": label,
            "what_was_right": ["Answer provided"],
            "what_was_missed": ["LLM evaluation unavailable — heuristic scoring used"],
            "misconception": None,
            "probe_suggestion": "Can you elaborate on your reasoning?",
            "next_difficulty_recommendation": "same",
        }


# Singleton
answer_evaluator = AnswerEvaluator()
