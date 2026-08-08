# PROBE — Interview Console

Frontend for **Problem Statement 2: The Interview Agent** (ABTalks Vibe Code Hackathon).
Pairs with the [`Interview-Agent` backend](https://github.com/Sajiree-2005/Interview-Agent) via the single
contract defined in `technical-spec.md`.

> "It reads the candidate's signal, not a script."

## What this is

A console-style interview UI, deliberately not the generic "chat bubble on a purple gradient" AI look.
The visual language is borrowed from oscilloscopes and lab instruments — a fitting metaphor for an agent
that treats an interview as a signal to be read (competency, evidence, coverage) rather than a script to run.

- **Landing** — pick a candidate from the roster, see real progress data (missions completed, commit days,
  first-try passes, skipped topics) and the actual 31-day / 8-module curriculum rendered as an isometric
  module rack.
- **Interview** — a live chat transcript on the left, an instrument sidebar on the right (question counter,
  live signal trace, session timer), talking to the backend exclusively through `POST /api/interview`.
- **Results** — the evidence-backed feedback report (`summary`, `strengths`, `gaps`, `next`) per the spec.

## Motion

All animation is done with [Anime.js v4](https://animejs.com) — no other animation runtime:
- A hand-built SVG **signal line** draws itself in and breathes gently; amplitude is derived from the
  candidate's real completion percentage, not decorative.
- The **module rack** uses real `curriculum.json` module data, entrance-staggers in via `onScroll`, and sits
  in real 3D space (`transform-style: preserve-3d`, `rotateX`).
- The candidate profile panel **tilts in 3D** with the mouse (`TiltPanel.jsx`) using live `rotateX/rotateY`
  transforms — no external 3D library needed for this depth of effect.
- Chat messages, number readouts, and page transitions all use `animate()` / `stagger()`.

`prefers-reduced-motion` is respected globally (see `src/styles/index.css`).

## Getting started

```bash
npm install
cp .env.example .env   # point VITE_API_URL at your backend
npm run dev
```

Build for production:

```bash
npm run build
npm run preview
```

## Backend contract

This app speaks **only** to `POST {VITE_API_URL}/api/interview`, exactly as defined in `technical-spec.md`:

```jsonc
// start
{ "sessionId": "…", "candidate": { /* candidate.json shape */ } }
// continue
{ "sessionId": "…", "message": "…" }
// responses
{ "reply": "…", "done": false }
{ "reply": "…", "done": true, "feedback": { "summary": "", "strengths": [], "gaps": [], "next": [] } }
```

See `src/api.js` for the client and `src/components/Interview.jsx` for the session flow.

## Project structure

```
src/
  api.js                  interview API client (start / continue)
  App.jsx                 landing → interview → results routing (state machine)
  components/
    Landing.jsx            candidate roster, hero, curriculum map
    Interview.jsx           session orchestration + layout
    ChatLog.jsx              transcript
    SidePanel.jsx            instrument sidebar
    Results.jsx              feedback report
    SignalLine.jsx           signature animated waveform
    ModuleStack.jsx          3D isometric curriculum rack
    TiltPanel.jsx            mouse-driven 3D tilt wrapper
    NumberReadout.jsx        animated count-up numbers
  data/
    candidates.json          candidate roster (from the hackathon dataset)
    curriculum.json          31-day curriculum (from the hackathon dataset)
```

## Deployment

Any static host works (Vercel, Netlify). Set `VITE_API_URL` as a build-time environment variable pointing at
the deployed FastAPI backend (Render/Railway/Fly, per the backend's own README).

## AI usage

See `PROMPTS.md` for the AI development log required by the hackathon rules.
