# Interview Intelligence Engine — PROBE

> An evidence-driven AI interview agent that goes beyond asking questions — it understands, adapts,
> probes, and evaluates. Built for the ABTalks Vibe Code Hackathon, Problem Statement 2: The Interview
> Agent.

This is a two-part monorepo:

| Folder | What it is | Docs |
|---|---|---|
| `interview-agent-backend/` | FastAPI + RAG + LLM interview engine | [backend README](./interview-agent-backend/README.md) |
| `frontend/` | React + Tailwind + Anime.js "PROBE" console UI | [frontend README](./frontend/README.md) |

The two talk to each other through exactly one endpoint, defined in `technical-spec.md`:
`POST /api/interview`.

## Run it locally (both halves, in order)

**1. Backend first** — the frontend has nothing to talk to without it.

```bash
cd interview-agent-backend
python -m venv .venv
.venv\Scripts\activate        # Windows: .venv\Scripts\activate · macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env        # macOS/Linux: cp .env.example .env
# edit .env and set a real OPENAI_API_KEY with available quota
uvicorn app.main:app --reload --port 8000
```

Confirm it's actually up before touching the frontend: open `http://localhost:8000/health` — you should
see `{"status":"ok","rag_ready":true}`. The first run downloads a small embedding model from Hugging
Face, so give it 30-60 seconds.

**2. Frontend second**, in a separate terminal:

```bash
cd frontend
npm install
copy .env.example .env        # macOS/Linux: cp .env.example .env
# .env should contain: VITE_API_URL=http://localhost:8000
npm run dev
```

Open the printed local URL, pick a candidate, and run a full interview through to the feedback report.

## Deploying

- **Backend -> Render.** A `render.yaml` Blueprint is provided at the repo root (`rootDir:
  interview-agent-backend`). If deploying manually via the Render dashboard instead of a Blueprint, set
  **Root Directory** to `interview-agent-backend` explicitly, or the build will fail looking for
  `requirements.txt` in the wrong place. Set `OPENAI_API_KEY` (with real quota) in Render's environment
  variables -- it's marked `sync: false` in the Blueprint so it must be entered manually, never committed.
- **Frontend -> Vercel.** Import the repo, set **Root Directory** to `frontend` in the Vercel project
  settings, and add an environment variable `VITE_API_URL` pointing at the deployed Render backend URL
  (e.g. `https://interview-agent-backend.onrender.com`) -- no trailing slash. A `vercel.json` is included
  for explicit build settings.

Redeploy the frontend after changing `VITE_API_URL` -- Vite bakes environment variables in at build time,
not at runtime.

## Deliverables checklist

- [x] Landing page with candidate selection
- [x] Curriculum ingestion (`curriculum.json` -> RAG index)
- [x] Candidate profile ingestion (`candidates.json` -> analysis)
- [x] RAG over curriculum (embeddings + retrieval; see note below)
- [x] Adaptive interview engine (difficulty steps up/down per answer)
- [x] Conversation memory (per-session, in-process)
- [x] At least 8 questions across at least 4 curriculum days (enforced in `interview_agent.py`)
- [x] Intelligent follow-up questions (`probe_suggestion`, `next_difficulty_recommendation`)
- [x] Structured feedback report (`summary`, `strengths`, `gaps`, `next`, plus a richer `fingerprint` +
      `coverage` breakdown the frontend also renders)
- [x] Required HTTP endpoint from `technical-spec.md` (`POST /api/interview`)
- [ ] Deployed frontend and backend -- deploy using the steps above
- [ ] Public GitHub repository with `PROMPTS.md` -- push this repo; both `frontend/PROMPTS.md` and
      `interview-agent-backend/PROMPTS.md` exist, keep both updated with real prompts as you go

**Note on RAG storage:** the retriever (`app/rag/retriever.py`) uses NumPy cosine similarity over
Sentence-Transformer embeddings rather than literally integrating FAISS or Chroma. For 31 curriculum
days this is functionally equivalent -- same embedding step, same top-k retrieval -- and it removes a
native-dependency install risk on Render. If a literal FAISS/Chroma integration is required for judging
criteria, that's a scoped, isolated swap in `retriever.py` alone.
