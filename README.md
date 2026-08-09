# PROBE — Interview Agent

**Hackathon:** ABTalks Vibe Code Hackathon — Problem Statement 2: The Interview Agent  
**Team:** InnoQueens  
**Live Demo:** [https://interview-agent-epvq71sf2-sajirees-projects.vercel.app/](https://interview-agent-epvq71sf2-sajirees-projects.vercel.app/)  
**Backend:** [https://interview-agent-yl3i.onrender.com](https://interview-agent-yl3i.onrender.com)  

---

## What is PROBE?

PROBE is a full-stack adaptive AI interview system. The **backend** is an evidence-driven interview agent that reads a candidate's learning journey, builds a personalized strategy, and dynamically probes their depth. The **frontend** is an oscilloscope-style interview console that treats the interview as a signal to be read — not a script to run.

> "It reads the candidate's signal, not a script."

---

## Monorepo Structure

```
├── backend/                 # FastAPI adaptive interview engine
│   ├── app/
│   │   ├── api/
│   │   │   └── interview.py         # POST /api/interview
│   │   ├── agents/
│   │   │   ├── interview_agent.py   # Main orchestrator
│   │   │   ├── strategy_engine.py   # Interview blueprint generation
│   │   │   └── question_planner.py  # Curriculum-grounded question gen
│   │   ├── evaluation/
│   │   │   ├── answer_evaluator.py  # Multi-dimensional LLM evaluation
│   │   │   ├── competency_engine.py # Evidence-based scoring
│   │   │   └── contradiction_detector.py
│   │   ├── rag/
│   │   │   ├── embeddings.py        # Pre-computed TF-IDF embeddings
│   │   │   └── retriever.py         # Numpy cosine similarity retrieval
│   │   ├── memory/
│   │   │   └── interview_memory.py  # Session state + competency tracking
│   │   ├── services/
│   │   │   ├── curriculum_service.py
│   │   │   └── candidate_service.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   └── core/
│   │       ├── config.py
│   │       └── logging.py
│   ├── data/
│   │   ├── curriculum.json
│   │   ├── candidates.json
│   │   ├── curriculum_embeddings.npy
│   │   └── curriculum_day_map.json
│   ├── tests/
│   ├── deploy/
│   │   └── render.yaml
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/                # Vite + React interview console
│   ├── src/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── Landing.jsx
│   │   │   ├── Interview.jsx
│   │   │   ├── ChatLog.jsx
│   │   │   ├── SidePanel.jsx
│   │   │   ├── Results.jsx
│   │   │   ├── SignalLine.jsx
│   │   │   ├── ModuleStack.jsx
│   │   │   ├── TiltPanel.jsx
│   │   │   └── NumberReadout.jsx
│   │   ├── data/
│   │   │   ├── candidates.json
│   │   │   └── curriculum.json
│   │   └── styles/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── vercel.json
│   └── README.md
│
├── PROMPTS.md               # AI usage log (hackathon requirement)
└── README.md                # This file
```

---

## Backend — Interview Intelligence Engine

### Problem

Technical interviews are often generic, repetitive, and fail to adapt to what a candidate actually knows. Most AI interviewers are simple question generators that don't understand the candidate's learning journey, don't remember the conversation, and don't probe deeper when a candidate shows strength or scaffold when they struggle.

### Solution

An **evidence-driven adaptive interview agent** that:
- Builds an **Interview Blueprint** before asking a single question
- Uses **Curriculum RAG** to ground every question in actual learning material
- Maintains an **Evidence-Based Competency Model** with per-topic dimensions
- Adapts difficulty dynamically based on multi-signal evaluation
- Detects **technical contradictions** across the conversation
- Generates **explainable, personalized feedback** with a 7-day learning path

### Architecture

```
Candidate Profile → Candidate Analyzer → Strategy Engine → Interview Blueprint
                                                          ↓
                    ┌──────────────┬──────────────┬──────────────┐
                    ▼              ▼              ▼              ▼
               Curriculum      Question       Answer       Competency
                  RAG          Planner       Evaluator       Engine
                    │              │              │              │
                    └──────────────┴──────────────┴──────────────┘
                                                  ↓
                                    Memory Update + Contradiction Detection
                                                  ↓
                                          Strategy Replanning
                                                  ↓
                                    Next Question or Final Feedback
```

### Core Features

| Feature | Description |
|---------|-------------|
| Interview Strategy Engine | Generates per-candidate blueprints from learning history |
| Curriculum RAG | Pre-computed TF-IDF embeddings with numpy cosine retrieval |
| Adaptive Questioning | Difficulty and type adapt based on 6-dimension evaluation |
| Competency Model | Per-topic scoring: conceptual, practical, reasoning, system design, communication, confidence |
| Dynamic Difficulty | Foundational → Intermediate → Advanced → Expert |
| Scenario Questioning | Prioritizes debugging, trade-off, and system-design questions |
| Contradiction Detection | Semantic consistency checking across conversation |
| Memory | Short-term conversation + structured competency memory |
| Personalized Feedback | Final report with strengths, gaps, and 7-day learning path |

### API Contract

```
POST /api/interview
```

**Start Interview**
```json
{
  "sessionId": "abc-123",
  "candidate": { /* full candidate.json shape */ }
}
```

**Continue Interview**
```json
{
  "sessionId": "abc-123",
  "message": "Candidate answer here"
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
    "next": [],
    "fingerprint": { /* optional: competency scores */ },
    "coverage": { /* optional: days/topics/types covered */ }
  }
}
```

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: OPENAI_API_KEY=sk-your-key-here
uvicorn app.main:app --reload --port 8000
```

### Backend Testing

```bash
cd backend
pytest tests/ -v
```

### Backend Deployment (Render)

1. Push `backend/` to your repo
2. On Render → **New Web Service** → Connect repo
3. Set **Blueprint Path** to `deploy/render.yaml` (or move `render.yaml` to root)
4. Add environment variable: `OPENAI_API_KEY=sk-your-key`
5. Deploy

**Note:** We use pre-computed TF-IDF embeddings (shipped in `data/`) instead of loading `torch`/`sentence-transformers` at runtime. This keeps memory under Render's 512MB limit.

---

## Frontend — PROBE Interview Console

### What this is

A console-style interview UI, deliberately not the generic "chat bubble on a purple gradient" AI look. The visual language is borrowed from oscilloscopes and lab instruments — a fitting metaphor for an agent that treats an interview as a signal to be read.

- **Landing** — pick a candidate from the roster, see real progress data, and the actual 31-day / 8-module curriculum rendered as an isometric module rack.
- **Interview** — a live chat transcript on the left, an instrument sidebar on the right (question counter, live signal trace, session timer).
- **Results** — the evidence-backed feedback report with animated competency score cards and curriculum coverage map.

### Motion

All animation is done with [Anime.js v4](https://animejs.com) — no other animation runtime:
- A hand-built SVG **signal line** draws itself in and breathes gently; amplitude derived from the candidate's real completion percentage.
- The **module rack** uses real `curriculum.json` module data, entrance-staggered via `onScroll`, sitting in real 3D space (`transform-style: preserve-3d`, `rotateX`).
- The candidate profile panel **tilts in 3D** with the mouse (`TiltPanel.jsx`) using live `rotateX/rotateY` transforms.
- Chat messages, number readouts, and page transitions all use `animate()` / `stagger()`.

`prefers-reduced-motion` is respected globally.

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env: VITE_API_URL=https://interview-agent-yl3i.onrender.com
npm run dev
```

### Frontend Build

```bash
cd frontend
npm run build
npm run preview
```

### Frontend Deployment (Vercel)

1. Push `frontend/` to your repo
2. On [vercel.com/new](https://vercel.com/new) → Import repo
3. Framework preset: **Vite**
4. Add environment variable: `VITE_API_URL=https://interview-agent-yl3i.onrender.com`
5. Deploy

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | — | OpenAI or compatible API key |
| `OPENAI_BASE_URL` | No | `https://api.openai.com/v1` | API base URL |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | Main model |
| `EVAL_MODEL` | No | `gpt-4o-mini` | Evaluation model |
| `APP_ENV` | No | `development` | production/development |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### Frontend (`frontend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | Yes | Backend URL (e.g. `https://interview-agent-yl3i.onrender.com`) |

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **TF-IDF + numpy** instead of FAISS/torch | Render 512MB memory limit; Python 3.13 wheel gaps for `faiss-cpu` |
| **Pre-computed embeddings** | Eliminates 400MB runtime model load; instant startup |
| **In-memory sessions** | Sufficient for hackathon; Redis would be a production upgrade |
| **OpenAI-compatible client** | Swappable to Groq, Azure, or any compatible provider via env vars |
| **Single `POST /api/interview`** | Matches `technical-spec.md` exactly; state via `sessionId` |
| **Oscilloscope UI** | Differentiator from generic AI chat UIs; grounded in product metaphor |
| **Anime.js v4 only** | One animation runtime, no bloat; `prefers-reduced-motion` respected |
| **Vite + React** | Fast dev server, optimized builds, straightforward deployment |

---

## AI Usage

See [`PROMPTS.md`](./PROMPTS.md) for the complete AI development log required by the hackathon rules. It covers every significant build session, debugging iteration, design decision, and runtime prompt used by both backend and frontend.

---

## Submission Checklist

- [x] Public repository accessible
- [x] Live demo URL functional (Vercel frontend + Render backend)
- [x] `PROMPTS.md` included at repo root
- [x] Backend API matches `technical-spec.md`
- [x] Frontend consumes backend via single `POST /api/interview`
- [x] All content grounded in real `curriculum.json` and `candidates.json` data
- [x] Commit history shows incremental development during hackathon
