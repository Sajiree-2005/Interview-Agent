# PROMPTS.md — AI Usage Log

Required deliverable per the ABTalks Vibe Code Hackathon rules ("A PROMPTS.md in the repo… this is how we
verify the build was genuinely vibe-coded"). This documents the AI-assisted development of the **frontend**
(`probe-frontend`). Keep appending to this file as you keep prompting — judges want the real trail, not a
cleaned-up version.

---

## Session 1 — Frontend scaffold (Claude)

**Context given to the model:** the ABTalks hackathon submission page, problem-statement docs
(`candidates.json`, `curriculum.json`, `technical-spec.md`), and the teammate's backend repo
(`github.com/Sajiree-2005/Interview-Agent`) as the API contract source of truth.

**Prompt (paraphrased from the actual request):**
> Analyse the hackathon rules and the teammate's backend repo. Build the frontend only — must not look like a
> generic AI chat UI, needs real 3D animation and scroll effects, must be unique enough to win, and all
> content must be accurate against the provided data and API spec.

**What the model did:**
1. Fetched the hackathon page, the backend README, and both animation-library links to ground the build in
   real constraints (deadline, deliverables, exact API contract, available motion tooling).
2. Flagged that one of the two animation links supplied (`animmasterlib.dev`) is a paid component marketplace
   with suspicious "switch to your phone" pop-up tactics — not a real free library — and used **Anime.js v4**
   (the other, legitimate link) as the only animation runtime instead.
3. Designed a distinct visual language (oscilloscope / lab-instrument console, not the default dark+neon or
   cream+terracotta AI look) grounded in the actual subject: an interview agent that "reads a signal."
4. Scaffolded a Vite + React + Tailwind project, wired it to the exact `POST /api/interview` contract from
   `technical-spec.md`, and built Landing / Interview / Results screens using the real `candidates.json` and
   `curriculum.json` data (no placeholder content).
5. Ran `npm install` and `npm run build` to confirm the project compiles cleanly before handing it off.

**Not done by AI in this session:** connecting to a live deployed backend, cross-browser QA, and any
copy/design changes made after this point — log those below as you make them.

---

## Session 2 — <your entry here>

Prompt:
Response summary:
Files touched:

---

## Session 3 — <your entry here>
