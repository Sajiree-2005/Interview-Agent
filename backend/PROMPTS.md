# Prompts Documentation

This document contains the major prompts used by the Interview Intelligence Engine.

## 1. Answer Evaluation Prompt

```
You are a senior technical interviewer evaluating a candidate's answer.

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

Respond ONLY as valid JSON.
```

## 2. Question Generation Prompt

```
You are an expert technical interviewer. Generate ONE interview question.

## Curriculum Context
{curriculum_context}

## Target Day
Day {day}: {title}
Tools: {tools}
Objectives: {objectives}

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

Respond ONLY as valid JSON with question, topic, day, difficulty, question_type, rationale, expected_concepts.
```

## 3. Strategy Blueprint Generation

Handled programmatically by `strategy_engine.py` using structured analysis of:
- passed/failed/skipped days
- attempt counts
- first-try ratios
- experience tier
- education and role

## 4. Contradiction Detection

Handled via semantic pattern matching in `contradiction_detector.py` with topic-specific contradiction pairs and conservative semantic checks.

## 5. Feedback Generation

Handled programmatically by aggregating:
- Competency scores with evidence
- Strength/gap identification
- Curriculum coverage tracking
- Personalized learning path construction
