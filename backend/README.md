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

```
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
```

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

```
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
```

## API Documentation

### `POST /api/interview`

**Start Interview**
```json
{
  "sessionId": "abc-123",
  "candidate": { ... }
}
```

**Continue Interview**
```json
{
  "sessionId": "abc-123",
  "message": "My answer here..."
}
```

**Response (in-progress)**
```json
{
  "reply": "Next question text...",
  "done": false
}
```

**Response (complete)**
```json
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
```

### `GET /health`

Returns service status and RAG readiness.

## Setup

```bash
# Clone and enter directory
<<<<<<< HEAD
cd backend
=======
cd interview-agent-backend
>>>>>>> 1cebba1fae7abec8708468eabe3b9e6ca8d5a5c5

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| OPENAI_API_KEY | Yes | - | OpenAI or compatible API key |
| OPENAI_BASE_URL | No | https://api.openai.com/v1 | API base URL |
| OPENAI_MODEL | No | gpt-4o-mini | Main model for generation |
| EVAL_MODEL | No | gpt-4o-mini | Model for evaluation |
| APP_ENV | No | development | production/development |
| LOG_LEVEL | No | INFO | Logging level |
| MAX_QUESTIONS | No | 10 | Interview upper limit |
| MIN_QUESTIONS | No | 8 | Interview lower limit |
| MIN_CURRICULUM_DAYS | No | 4 | Minimum day coverage |

## Running Locally

```bash
# Development with auto-reload
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Deployment

### Render (Recommended)

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect your repository
4. Set environment variables in Render Dashboard:
   - `OPENAI_API_KEY`
   - `APP_ENV=production`
5. Render will auto-detect `render.yaml` or use:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Vercel

Vercel is optimized for serverless/frontend. For this FastAPI backend, use **Render**, **Railway**, or **Fly.io** instead. If you must use Vercel, wrap with a serverless adapter (not recommended for stateful interview sessions).

### Docker

```bash
docker build -t interview-agent .
docker run -p 8000:8000 --env-file .env interview-agent
```

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app factory
│   ├── api/
│   │   └── interview.py        # POST /api/interview
│   ├── agents/
│   │   ├── interview_agent.py  # Main orchestrator
│   │   ├── strategy_engine.py  # Blueprint generation
│   │   └── question_planner.py # Question generation + validation
│   ├── evaluation/
│   │   ├── answer_evaluator.py # LLM-based evaluation
│   │   ├── competency_engine.py# Evidence-based scoring
│   │   └── contradiction_detector.py
│   ├── rag/
│   │   ├── embeddings.py       # Sentence-transformers
│   │   └── retriever.py        # FAISS index
│   ├── memory/
│   │   └── interview_memory.py # Session state management
│   ├── services/
│   │   ├── curriculum_service.py
│   │   └── candidate_service.py
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   └── core/
│       ├── config.py           # Settings
│       └── logging.py          # Structured logging
├── data/
│   ├── curriculum.json
│   └── candidates.json
├── tests/
├── deploy/
│   └── render.yaml
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── PROMPTS.md
```

## Design Decisions

1. **FAISS over Chroma/Pinecone**: Zero external dependency, fast in-memory search, sufficient for 31 curriculum days
2. **Single endpoint API**: Matches hackathon spec exactly; state managed via sessionId
3. **OpenAI-compatible client**: Works with OpenAI, Groq, Azure, or any compatible provider
4. **In-memory session store**: Sufficient for hackathon; can be swapped for Redis in production
5. **Structured LLM outputs**: JSON-mode evaluation ensures reliable parsing and scoring
6. **Deterministic + LLM hybrid**: Strategy and competency use deterministic rules; question generation and evaluation use LLM

## Limitations

- Session state is in-memory (lost on restart). For production at scale, migrate to Redis.
- FAISS index rebuilds on startup. For large curricula, persist to disk.
- Contradiction detection uses conservative heuristics; full semantic NLI would be more accurate but slower.
- Requires external LLM API (cost incurred per evaluation/generation).

## Future Improvements

- Redis-backed session persistence
- Persistent FAISS index with incremental updates
- Full LLM-based contradiction detection using NLI models
- Voice/video interview support
- Real-time interviewer dashboard
- A/B testing framework for question effectiveness
- Multi-language interview support
