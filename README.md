# Interview Intelligence Engine

## Problem

Technical interviews are often generic, repetitive, and fail to adapt to what a candidate actually knows. Most AI interviewers are simple question generators that don't understand the candidate's learning journey, don't remember the conversation, and don't probe deeper when a candidate shows strength or scaffold when they struggle.

## Solution

The Interview Intelligence Engine is an **evidence-driven adaptive interview agent** that constructs a personalized interview strategy from a candidate's learning journey, continuously updates its competency model from their responses, and dynamically probes their conceptual depth, engineering judgment, and system-design ability.

## Key Innovation

Unlike generic "AI interview me" chatbots, this system:
- Builds an **Interview Blueprint** before asking a single question
- Uses **Curriculum RAG** to ground every question in actual learning material
- Maintains an **Evidence-Based Competency Model** with per-topic dimensions
- Adapts difficulty dynamically based on multi-signal evaluation
- Detects **technical contradictions** across the conversation
- Generates **explainable, personalized feedback** with a 7-day learning path

## Architecture
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│Candidate Profile│────▶│Candidate Analyzer│────▶│Strategy Engine  │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
│
┌───────────────────────────┘
▼
┌──────────────────┐
│Interview Blueprint│
└────────┬─────────┘
│
┌──────────────┼──────────────┐
▼              ▼              ▼
┌─────────┐   ┌──────────┐   ┌──────────┐
│Curriculum│   │Question  │   │Answer    │
│RAG (FAISS)│   │Planner   │   │Evaluator │
└────┬────┘   └────┬─────┘   └────┬─────┘
│             │              │
└─────────────┴──────────────┘
│
▼
┌──────────────┐
│Competency    │
│Engine        │
└──────┬───────┘
│
┌────────────┼────────────┐
▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌──────────┐
│Memory   │  │Contradiction│  │Strategy │
│Update   │  │Detection    │  │Replan   │
└─────────┘  └─────────┘  └──────────┘
│
▼
┌──────────────┐
│Next Question │
│or Final      │
│Feedback      │
└──────────────┘
plain

## Core Features

| Feature | Description |
|---------|-------------|
| Interview Strategy Engine | Generates per-candidate blueprints based on learning history |
| Curriculum RAG | FAISS-based retrieval grounding questions in actual curriculum |
| Adaptive Questioning | Difficulty and type adapt based on evaluation signals |
| Competency Model | 6-dimension per-topic scoring with evidence tracking |
| Dynamic Difficulty | Foundational → Intermediate → Advanced → Expert progression |
| Scenario Questioning | Prioritizes debugging, trade-off, and system-design questions |
| Contradiction Detection | Semantic consistency checking across conversation |
| Memory | Short-term conversation + structured competency memory |
| Personalized Feedback | Final report with strengths, gaps, and 7-day learning path |

## AI Architecture

- **LLM**: OpenAI-compatible API (GPT-4o-mini default, configurable)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector DB**: FAISS (in-memory, cosine similarity)
- **RAG**: Dense retrieval over curriculum days with metadata
- **Memory**: In-memory session store with structured state
- **Evaluation**: Structured LLM-based multi-dimensional scoring

## Interview Flow
Candidate submits profile
↓
Profile Analysis (attempts, passes, skips, experience)
↓
Interview Blueprint generated
↓
Question 1 (grounded in curriculum RAG)
↓
Candidate Answer
↓
Multi-dimensional Evaluation
↓
Competency Update + Contradiction Check
↓
Strategy Adaptation
↓
Question 2...N
↓
Final Structured Feedback + Learning Path
plain

## API Documentation

### `POST /api/interview`

**Start Interview**
```json
{
  "sessionId": "abc-123",
  "candidate": { ... }
}
Continue Interview
JSON
{
  "sessionId": "abc-123",
  "message": "My answer here..."
}
Response (in-progress)
JSON
{
  "reply": "Next question text...",
  "done": false
}
Response (complete)
JSON
{
  "reply": "Interview completed.",
  "done": true,
  "feedback": {
    "summary": "...",
    "strengths": [],
    "gaps": [],
    "next": []
  }
}
GET /health
Returns service status and RAG readiness.
Setup
bash
# Clone and enter directory
cd interview-agent-backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
