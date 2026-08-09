# Prompts Documentation

This document describes how the frontend (`PROBE — Interview Console`) was built with AI assistance
(Claude), in the same spirit as the backend's `PROMPTS.md`: not the runtime prompts an LLM sees, but the
build prompts and technical decisions that produced this codebase.

## 1. Initial Build Prompt

```
Analyse the hackathon rules and the teammate's backend repo. Build the frontend only — must not look
like a generic AI chat UI, needs real 3D animation and scroll effects, must be unique enough to win,
and all content must be accurate against the provided data and API spec.
```

Grounding used before writing any code:
- The hackathon submission page (deliverables: public repo, live URL, `PROMPTS.md`).
- `technical-spec.md` — the authoritative API contract (`POST /api/interview`, session-driven).
- The backend repo itself, to confirm request/response shapes and available feedback fields.
- `candidates.json` / `curriculum.json` — real data, not placeholders, throughout the UI.
- Both animation-library links supplied by the user. One (`animmasterlib.dev`) turned out to be a paid
  component marketplace with manipulative pop-up tactics, not a free library — it was rejected in favor
  of the other, legitimate link (Anime.js v4), which became the only animation runtime used.

## 2. Design System Prompt

```
Design a visual language for an AI interview agent that is explicitly NOT the generic dark-mode /
purple-gradient / chat-bubble AI product look. Ground it in the product's own pitch: "reads a
candidate's signal, not a script."
```

Output: an oscilloscope / lab-instrument console aesthetic —
- Graphite background (`#0B0E13`), amber signal accent (`#FFB454`), teal secondary (`#5FE3C4`), coral
  reserved only for "gap"/error states — color is functional (competency meaning), not decorative.
- `Space Grotesk` for headlines, `IBM Plex Sans` for body copy, `IBM Plex Mono` for every numeric
  readout (question counter, session timer, competency %) — monospace used deliberately, like an
  instrument panel.
- A signature animated SVG "signal line" whose amplitude is derived from real candidate completion data,
  reused across Landing, the live interview sidebar, and the Results report for visual continuity.

## 3. API Integration Prompt

```
Wire this UI to the single required endpoint exactly as defined in technical-spec.md. Handle both the
minimal spec-guaranteed feedback fields and any richer optional fields the backend happens to return,
without breaking if they're absent.
```

Implementation: `src/api.js` posts only `{ sessionId, candidate }` then `{ sessionId, message }` to
`POST {VITE_API_URL}/api/interview`. `Results.jsx` renders `summary/strengths/gaps/next` unconditionally
(per spec) and additionally renders the backend's `fingerprint` (competency score cards) and `coverage`
(curriculum-day map, question-type breakdown) when present — since this backend's `_generate_feedback()`
genuinely returns both, and they're the most distinctive evidence the product produces.

## 4. Animation System Prompt

```
Real 3D and scroll-triggered motion, Anime.js only, no other animation runtime, respect
prefers-reduced-motion.
```

- `SignalLine.jsx` — SVG path draw-in (`strokeDashoffset`) plus an ambient breathing loop.
- `ModuleStack.jsx` — an isometric 3D rack of the real 8 curriculum modules
  (`transform-style: preserve-3d`, `rotateX`), entrance-staggered via Anime's `onScroll`. Reused with a
  different highlight color for candidate progress (Landing) vs. actual interview coverage (Results).
- `TiltPanel.jsx` — live mouse-driven `rotateX/rotateY` 3D tilt on the candidate profile panel.
- `ScoreCards.jsx` / `NumberReadout.jsx` — animated count-up numeric readouts via `animate()` +
  `onUpdate`.

## 5. Debugging Log

**Session: "cannot fetch backend" error.** Traced to the browser never reaching `localhost:8000` at
all — isolated by hitting `/health` directly, confirming `.env`/dev-server restart requirements (Vite
only reads `.env` at startup), and confirming Windows-specific gotchas (hidden `.env.txt` extensions).
No frontend code changes were needed; the fetch client was already failing correctly and reporting a
clear error.

**Session: interview fails on the first evaluated answer.** Backend log showed a Pydantic
`ValidationError` — `TopicCompetency.dimensions` had no default, so `competency_engine.py` crashed the
moment it scored a new topic, independent of and in addition to a separate OpenAI quota (`429
insufficient_quota`) issue on the same run. Root-caused by reading `schemas.py` and
`competency_engine.py` directly; fixed by giving `dimensions` a `default_factory` in the schema so every
construction path is safe, not just the one call site that happened to trigger it.

## 6. <your entry here>

Prompt:
Response summary:
Files touched:
