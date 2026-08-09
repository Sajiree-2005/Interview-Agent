# AI Usage Log — PROBE Interview Agent

**Project:** PROBE — Interview Console + Interview Intelligence Engine  
**Hackathon:** ABTalks Vibe Code Hackathon — Problem Statement 2: The Interview Agent  
**AI Tools Used:** Claude (Anthropic), ChatGPT (OpenAI)  
**Team Role:** Senior AI Backend Engineer + Frontend Developer  

---

## Overview

This document records every significant AI-assisted build session that produced this project. It covers both the **backend** (FastAPI adaptive interview agent with curriculum-grounded RAG, competency tracking, and dynamic difficulty) and the **frontend** (oscilloscope-style interview console with real 3D animation). The log is organized chronologically by build phase, with exact prompts, grounding data, and debugging iterations preserved.

---

## Phase 1: Backend Architecture & Foundation

### 1.1 Initial Scoping Prompt

> **To:** Claude  
> **Context:** Full hackathon brief, `technical-spec.md`, `curriculum.json`, `candidates.json`  
> **Prompt:**  
> "You are a Senior AI Backend Engineer, Agent Architect, and Production ML Engineer. Build the entire AI intelligence + backend layer of our hackathon project. Before implementing anything, inspect `curriculum.json`, `candidates.json`, and `technical-specs.md` — these are the source of truth. Do NOT assume their schemas.  
>   
> Build an adaptive AI technical interviewer that understands what a candidate has learned, builds an interview strategy, listens to their answers, evaluates their technical reasoning, remembers the conversation, and dynamically decides what to ask next. The final experience should feel like a strong human technical interviewer, not an LLM wrapper.  
>   
> Requirements: intelligent, personalized, curriculum-grounded, adaptive, conversational, technically rigorous, explainable, reliable, modular, production-quality. Do not implement generic placeholder logic. Do not hardcode a fixed sequence of questions. Build an actual interview decision system with a feedback loop.  
>   
> Deliver: complete FastAPI backend with all modules, tests, README, PROMPTS.md, and deployment config for Render."

**Grounding provided:**
- `curriculum.json` — 31-day / 8-module AI cohort curriculum
- `candidates.json` — 20 candidate profiles with missions, attempts, skips, signals
- `technical-spec.md` — single `POST /api/interview` endpoint contract
- Architecture diagram from brief (strategy engine → RAG → question planner → evaluator → memory → replanning)

**Output:** Complete project scaffold with 20+ files across `app/agents/`, `app/evaluation/`, `app/rag/`, `app/memory/`, `app/services/`, `app/models/`, `app/core/`.

---

### 1.2 Curriculum RAG & Embedding Pipeline

> **Prompt:**  
> "Build a proper curriculum retrieval pipeline: curriculum.json → normalization → semantic chunks → embeddings → vector store → retriever → relevant curriculum context. Use a lightweight reliable vector store. Every question must be grounded in the actual curriculum. Do not over-engineer the vector infrastructure."

**Decision:** FAISS was initially chosen, then replaced with pure numpy cosine similarity after discovering Render's 512MB memory limit and Python 3.13 wheel incompatibility for `faiss-cpu`. Pre-computed TF-IDF embeddings were generated offline and shipped in the repo to eliminate runtime model loading entirely.

**Files created:** `app/rag/embeddings.py`, `app/rag/retriever.py`, `data/curriculum_embeddings.npy`, `data/curriculum_day_map.json`

---

### 1.3 Evidence-Based Competency Model

> **Prompt:**  
> "Do not represent the candidate only with one score. Create a competency map. For each relevant competency maintain: conceptual_understanding, practical_application, engineering_reasoning, system_design, communication, confidence, evidence, confidence_in_assessment. Every major score should be supported by evidence from the conversation."

**Implementation:** `CompetencyDimension` Pydantic model with exponential moving average updates per evaluation. Evidence lists accumulate observed behaviors. `confidence_in_assessment` scales with amount of evidence.

**Files created:** `app/evaluation/competency_engine.py`, `app/models/schemas.py`

---

### 1.4 Answer Evaluation Engine

> **Prompt:**  
> "Every candidate answer should be evaluated internally. Evaluate at least: correctness, conceptual depth, practical understanding, engineering reasoning, trade-off awareness, communication clarity. Also determine: strong / acceptable / partial / weak / incorrect. Identify what the candidate got right, what they missed, what misconception they may have, whether deeper probing is warranted, and what question should come next. Do NOT expose chain-of-thought. Store concise structured evidence instead."

**Runtime prompt used by backend** (in `app/evaluation/answer_evaluator.py`):

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

---

### 1.5 Question Generation Prompt

> **Prompt:**  
> "Before a generated question reaches the candidate, validate it. Check: is it grounded in the curriculum? Does the topic actually exist? Does the curriculum day match? Is it appropriate to the candidate? Has the concept already been sufficiently tested? Is it genuinely different from previous questions? If validation fails: REJECT → REGENERATE. Also track question types and ensure diversity."

**Runtime prompt used by backend** (in `app/agents/question_planner.py`):

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

---

## Phase 2: Backend Debugging & Deployment

### 2.1 Python 3.13 Compatibility Crisis

**Problem:** `pydantic-core==2.18.4` has no pre-built wheels for Python 3.13. Render's default Python 3.14 made it worse. Build failed with Rust compilation errors.

**Prompt:**  
> "numpy install fails on Python 3.13. faiss-cpu also fails. Fix requirements.txt to be Python 3.13 compatible. Also pydantic-settings is missing."

**Fix applied:** Bumped `pydantic` to 2.9.2, `pydantic-settings` to 2.5.2, `fastapi` to 0.115.0. Replaced FAISS with numpy cosine similarity. Added `.python-version` file pinning Render to Python 3.12.3.

### 2.2 Out of Memory on Render

**Problem:** `torch` + `sentence-transformers` loaded ~400MB at startup, exceeding Render's 512MB limit. App crashed during embedding model download.

**Prompt:**  
> "Render says Out of memory (used over 512Mi). The embedding model is too heavy. How do I fix this without losing RAG functionality?"

**Fix applied:** Pre-computed TF-IDF embeddings offline using scikit-learn, saved as `.npy` and `.json` files in `data/`. Removed `sentence-transformers` and `torch` from requirements. At runtime, retriever loads pre-computed vectors and fits a lightweight TF-IDF vectorizer for query encoding only.

### 2.3 Import Error: QuestionRecord not in schemas

**Problem:** `interview_agent.py` imported `QuestionRecord` and `AnswerRecord` from `app.models.schemas`, but they are dataclasses in `app.memory.interview_memory`.

**Prompt:**  
> "It cannot find Question record and answer record in schema"

**Fix:** Removed incorrect imports from `schemas`, confirmed they only import from `memory`.

### 2.4 Pydantic ValidationError on First Evaluation

**Problem:** `TopicCompetency` required `dimensions` field with no default. When evaluator fell back to heuristic scoring (due to OpenAI quota exhaustion), competency engine crashed creating a new topic entry.

**Prompt:**  
> "Interview processing failed: ValidationError: 1 validation error for TopicCompetency dimensions Field required"

**Fix:** Added `default_factory=CompetencyDimension` to `dimensions` field in `TopicCompetency` schema. Improved fallback evaluation to handle quota errors explicitly.

---

## Phase 3: Frontend Design & Build

### 3.1 Initial Frontend Brief

> **To:** Claude  
> **Context:** Hackathon rules, teammate's backend repo, `technical-spec.md`, animation library links  
> **Prompt:**  
> "Analyse the hackathon rules and the teammate's backend repo. Build the frontend only — must not look like a generic AI chat UI, needs real 3D animation and scroll effects, must be unique enough to win, and all content must be accurate against the provided data and API spec."

**Grounding used:**
- Hackathon submission requirements (public repo, live URL, PROMPTS.md)
- `technical-spec.md` — single `POST /api/interview` contract
- Backend repo — request/response shapes, feedback fields (fingerprint, coverage)
- `candidates.json` / `curriculum.json` — real data throughout UI
- Animation libraries: one link was a paid component marketplace with manipulative pop-ups (rejected); Anime.js v4 was legitimate and became the sole animation runtime

### 3.2 Visual Language Design

> **Prompt:**  
> "Design a visual language for an AI interview agent that is explicitly NOT the generic dark-mode / purple-gradient / chat-bubble AI product look. Ground it in the product's own pitch: 'reads a candidate's signal, not a script.'"

**Output:** Oscilloscope / lab-instrument console aesthetic:
- Graphite background, amber signal accent, teal secondary
- Coral reserved only for error/gap states (functional color, not decorative)
- Space Grotesk headlines, IBM Plex Sans body, IBM Plex Mono for numeric readouts
- Signature animated SVG "signal line" whose amplitude derives from real candidate completion data

### 3.3 API Integration

> **Prompt:**  
> "Wire this UI to the single required endpoint exactly as defined in technical-spec.md. Handle both the minimal spec-guaranteed feedback fields and any richer optional fields the backend happens to return, without breaking if they're absent."

**Implementation:** `api.js` posts `{ sessionId, candidate }` then `{ sessionId, message }` to `POST {VITE_API_URL}/api/interview`. `Results.jsx` renders `summary/strengths/gaps/next` unconditionally (per spec) and additionally renders the backend's `fingerprint` (competency score cards) and `coverage` (curriculum-day map, question-type breakdown) when present.

### 3.4 Animation System

> **Prompt:**  
> "Real 3D and scroll-triggered motion, Anime.js only, no other animation runtime, respect prefers-reduced-motion."

**Components built:**
- `SignalLine.jsx` — SVG path draw-in plus ambient breathing loop
- `ModuleStack.jsx` — isometric 3D rack of real 8 curriculum modules, entrance-staggered via Anime's `onScroll`, `transform-style: preserve-3d`, `rotateX`
- `TiltPanel.jsx` — live mouse-driven 3D tilt on candidate profile panel
- `ScoreCards.jsx` / `NumberReadout.jsx` — animated count-up numeric readouts

---

## Phase 4: Frontend Debugging & Integration

### 4.1 Backend Connection Failure

**Problem:** Frontend showed "cannot fetch backend" error.

**Diagnosis:** Browser never reached `localhost:8000`. Isolated by hitting `/health` directly, confirming `.env` file and dev-server restart requirements. Windows-specific gotcha: hidden `.env.txt` extension.

**Resolution:** No frontend code changes needed. Fixed environment configuration.

### 4.2 Backend 500 on First Evaluated Answer

**Problem:** Interview failed after candidate submitted first answer. Browser showed 500.

**Diagnosis:** Backend log revealed two simultaneous issues:
1. OpenAI quota exhaustion (`429 insufficient_quota`)
2. `TopicCompetency.dimensions` had no default, causing Pydantic `ValidationError` when competency engine created a new topic entry

**Resolution:** Fixed in backend (`schemas.py` + `competency_engine.py`). Frontend `Results.jsx` was upgraded to render the backend's `fingerprint` and `coverage` data fields that were previously returned but unused.

### 4.3 Deployment Configuration

**Prompt:**  
> "Review every backend module against the team's stated responsibilities checklist. Apply the schemas.py fix directly. Add deployment configs for Render and Vercel. Rewrite the root README into a proper monorepo guide."

**Output:**
- `render.yaml` at repo root with `rootDir: backend`
- `frontend/vercel.json` for SPA routing
- Root `README.md` as monorepo guide linking to backend and frontend docs

---

## Runtime Prompts Summary

These are the actual prompts the backend sends to the LLM during live interviews:

| Prompt | Purpose | Location |
|--------|---------|----------|
| Answer Evaluation | Score candidate answer across 6 dimensions + label + evidence | `app/evaluation/answer_evaluator.py` |
| Question Generation | Generate curriculum-grounded question with rationale | `app/agents/question_planner.py` |
| Strategy Blueprint | Deterministic (no LLM) — candidate analysis → topic priorities | `app/agents/strategy_engine.py` |
| Contradiction Detection | Deterministic pattern matching + semantic checks | `app/evaluation/contradiction_detector.py` |
| Feedback Generation | Deterministic aggregation of competency scores + evidence | `app/agents/interview_agent.py` |

---

## Design Decisions & Trade-offs

| Decision | Rationale |
|----------|-----------|
| FAISS → numpy cosine similarity | Render memory limit (512MB) + Python 3.13 wheel gaps |
| sentence-transformers → TF-IDF | Eliminated 400MB torch load; pre-computed embeddings ship with repo |
| In-memory sessions | Sufficient for hackathon; Redis would be P3 improvement |
| OpenAI-compatible client | Works with OpenAI, Groq, Azure — swap via env vars |
| Single `POST /api/interview` endpoint | Matches `technical-spec.md` exactly; state via `sessionId` |
| Oscilloscope UI aesthetic | Differentiator from generic AI chat UIs; grounded in product metaphor |
| Anime.js v4 only | One animation runtime, no bloat; `prefers-reduced-motion` respected |

---

## Verification

- ✅ Public repository accessible
- ✅ Live demo URL functional (Vercel frontend + Render backend)
- ✅ This PROMPTS.md included at repo root
- ✅ All commit history shows incremental development during hackathon
- ✅ No imported codebase — built from scratch via AI-assisted sessions
