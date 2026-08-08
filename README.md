# Interview Intelligence Engine

> **An evidence-driven AI interview agent that goes beyond asking questions — it understands, adapts, probes, and evaluates.**

---

## Problem

Technical interviews are often generic, repetitive, and fail to adapt to what a candidate actually knows.

Most AI interviewers behave like simple question generators. They:

- Don't understand the candidate's learning journey
- Don't remember meaningful details from previous answers
- Ask questions in a fixed sequence
- Rarely probe deeper when a candidate demonstrates strong understanding
- Don't adapt when a candidate struggles
- Focus on definitions instead of engineering reasoning
- Provide generic feedback at the end

This creates an interview experience that feels scripted rather than realistic.

---

## Solution

The **Interview Intelligence Engine** is an **evidence-driven adaptive technical interview agent** that constructs a personalized interview strategy from a candidate's learning journey.

Throughout the interview, it continuously updates its understanding of the candidate based on their responses and dynamically decides what to ask next.

It evaluates:

- Conceptual understanding
- Practical application
- Engineering reasoning
- System-design ability
- Technical communication
- Depth of understanding

The goal is not simply to determine **what the candidate knows**, but to understand **how deeply they can reason about what they know**.

---

## Key Innovation

Unlike generic "AI interview me" chatbots, this system:

- Builds an **Interview Blueprint** before asking the first question
- Uses **Curriculum RAG** to ground questions in the actual learning material
- Maintains an **Evidence-Based Competency Model**
- Dynamically adapts question difficulty
- Uses **depth-over-definition questioning**
- Prioritizes scenario, debugging, architecture, and trade-off questions
- Detects meaningful **technical contradictions** across the conversation
- Maintains structured conversational memory
- Optimizes curriculum coverage
- Explains why a question was selected
- Generates evidence-backed feedback
- Produces a personalized **7-day learning path**

### Core Philosophy

> **Build the interviewer, not the interview.**

The system does not follow a predefined list of questions.

It continuously makes interview decisions based on candidate evidence.

---

# Architecture

```text
                    ┌─────────────────────┐
                    │  Candidate Profile  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Candidate Analyzer  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Strategy Engine    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Interview Blueprint │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌────────────┐   ┌─────────────┐   ┌─────────────┐
       │ Curriculum │   │   Question  │   │    Answer   │
       │ RAG /FAISS │   │   Planner   │   │  Evaluator  │
       └──────┬─────┘   └──────┬──────┘   └──────┬──────┘
              │                │                │
              └────────────────┼────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Competency Engine  │
                    └──────────┬──────────┘
                               │
               ┌───────────────┼────────────────┐
               │               │                │
               ▼               ▼                ▼
        ┌────────────┐  ┌──────────────┐  ┌─────────────┐
        │   Memory   │  │ Contradiction│  │  Strategy   │
        │   Update   │  │  Detection   │  │   Replan    │
        └────────────┘  └──────────────┘  └──────┬──────┘
                                                 │
                                                 ▼
                                      ┌────────────────────┐
                                      │   Next Question    │
                                      │         or         │
                                      │  Final Feedback    │
                                      └────────────────────┘
```

---

# Core Features

| Feature                       | Description                                                                        |
| ----------------------------- | ---------------------------------------------------------------------------------- |
| **Interview Strategy Engine** | Generates a personalized interview blueprint from the candidate's learning history |
| **Curriculum RAG**            | FAISS-based retrieval grounds questions in actual curriculum content               |
| **Adaptive Questioning**      | Question difficulty and type adapt according to candidate responses                |
| **Depth-Over-Definition**     | Progresses from concepts to application, trade-offs, and system design             |
| **Competency Model**          | Maintains multi-dimensional, evidence-based topic scores                           |
| **Dynamic Difficulty**        | Progresses between foundational, intermediate, advanced, and expert levels         |
| **Scenario Questioning**      | Tests debugging, architecture, practical application, and trade-off reasoning      |
| **Contradiction Detection**   | Identifies meaningful technical inconsistencies across answers                     |
| **Conversation Memory**       | Maintains both recent conversation and structured interview state                  |
| **Curriculum Coverage**       | Ensures minimum question and curriculum-day coverage requirements                  |
| **Question Grounding**        | Validates generated questions against the actual curriculum                        |
| **Question Diversity**        | Balances conceptual, scenario, debugging, trade-off, and system-design questions   |
| **Explainable Interviewing**  | Records why a question was selected and what competency it tests                   |
| **Personalized Feedback**     | Generates strengths, gaps, evidence, and actionable recommendations                |
| **7-Day Learning Path**       | Creates a personalized revision plan based on observed weaknesses                  |
| **Interview Fingerprint**     | Summarizes technical depth, reasoning, application, and communication              |

---

# AI Architecture

### LLM

**OpenAI-compatible API**

Default model:

```text
gpt-4o-mini
```

The model is configurable and can be replaced with another OpenAI-compatible provider.

---

### Embeddings

```text
sentence-transformers/all-MiniLM-L6-v2
```

Used to create semantic representations of curriculum content.

---

### Vector Database

```text
FAISS
```

FAISS provides lightweight, fast, in-memory similarity search and is sufficient for the relatively small 31-day curriculum.

---

### RAG

The curriculum is:

```text
Loaded
   ↓
Normalized
   ↓
Chunked
   ↓
Embedded
   ↓
Indexed in FAISS
   ↓
Retrieved during interview
```

Only relevant curriculum context is provided to the question-generation system.

---

### Memory

The system maintains:

#### Short-Term Memory

- Recent questions
- Recent answers
- Current topic
- Current difficulty
- Recent evaluation

#### Structured Memory

- Topics covered
- Curriculum days covered
- Strengths
- Weaknesses
- Misconceptions
- Technical contradictions
- Competency scores
- Evidence
- Remaining gaps

---

### Evaluation

Candidate responses are evaluated using structured LLM outputs across multiple dimensions:

- Correctness
- Conceptual understanding
- Practical application
- Engineering reasoning
- System-design ability
- Communication

The evaluation is combined with deterministic interview-state logic to decide the next step.

---

# Interview Flow

```text
Candidate Profile
       │
       ▼
Profile Analysis
       │
       ├── Completed Topics
       ├── Skipped Topics
       ├── Attempts
       └── Learning Signals
       │
       ▼
Interview Blueprint
       │
       ▼
Curriculum Retrieval
       │
       ▼
Question Generation
       │
       ▼
Question Validation
       │
       ▼
Candidate Answer
       │
       ▼
Multi-Dimensional Evaluation
       │
       ├── Correctness
       ├── Depth
       ├── Reasoning
       ├── Application
       └── Communication
       │
       ▼
Competency Update
       │
       ├── Memory Update
       ├── Contradiction Check
       └── Coverage Update
       │
       ▼
Strategy Replanning
       │
       ├── Go Deeper
       ├── Simplify
       ├── Change Topic
       └── Test Weak Area
       │
       ▼
Next Question
       │
       ▼
       ...
       │
       ▼
Final Evaluation
       │
       ├── Competency Report
       ├── Strengths
       ├── Weaknesses
       ├── Evidence
       ├── Curriculum Coverage
       └── Personalized Learning Path
```

---

# Adaptive Interviewing

The interviewer does not simply move from Question 1 to Question 2.

It adapts based on the candidate's response.

### Example

**Candidate:**

> "RAG retrieves relevant documents and provides them to the LLM."

The agent may respond:

> "Why would you choose RAG instead of fine-tuning for this use case?"

If the candidate answers well:

> "Your retrieval quality is poor despite good embeddings. What would you investigate first?"

If the candidate struggles:

> "Let's simplify that. What problem does retrieval solve in a RAG pipeline?"

This creates a progressive interview:

```text
Definition
    ↓
Understanding
    ↓
Application
    ↓
Debugging
    ↓
Trade-Off
    ↓
Architecture
    ↓
System Design
```

The depth is determined dynamically.

---

# Evidence-Based Competency Model

Instead of assigning a single generic score, the system maintains a competency profile for individual topics.

Example:

```json
{
  "topic": "Vector Databases",
  "conceptualUnderstanding": 0.88,
  "practicalApplication": 0.74,
  "engineeringReasoning": 0.69,
  "systemDesign": 0.61,
  "communication": 0.86,
  "confidence": 0.82,
  "evidence": [
    "Correctly explained embeddings",
    "Understood similarity search",
    "Struggled with indexing trade-offs"
  ]
}
```

This ensures that conclusions about the candidate are backed by observed evidence.

---

# Technical Contradiction Detection

The interviewer tracks important technical claims throughout the conversation.

If a candidate later gives an answer that meaningfully conflicts with an earlier claim, the system can probe the inconsistency.

Example:

**Earlier:**

> "We use RAG because the model cannot access our private documents."

**Later:**

> "The model already knows our private company documents."

The interviewer may respond:

> "Earlier you mentioned that RAG was necessary because the model could not access private documents. How do you reconcile that with your current explanation?"

The system uses conservative detection to avoid flagging harmless differences in wording.

---

# Question Strategy

The agent deliberately balances different question types:

| Question Type     | Purpose                         |
| ----------------- | ------------------------------- |
| **Conceptual**    | Test fundamental understanding  |
| **Application**   | Test ability to apply knowledge |
| **Scenario**      | Test practical decision-making  |
| **Debugging**     | Test problem-solving            |
| **Trade-off**     | Test engineering judgment       |
| **Architecture**  | Test system-level thinking      |
| **System Design** | Test deeper engineering ability |

This prevents the interview from becoming a sequence of definition questions.

---

# Curriculum Coverage

The challenge requires:

- At least **8 questions**
- At least **4 different curriculum days**

The system explicitly tracks:

```text
Questions Asked
Curriculum Days Covered
Topics Covered
Question Types
Topic Depth
Remaining Gaps
```

The strategy engine uses this state when selecting future questions.

---

# Final Feedback

At the end of the interview, the system generates an evidence-backed report containing:

### Overall Readiness

An overall score and readiness classification.

### Technical Strengths

Areas where the candidate demonstrated strong understanding.

### Technical Gaps

Areas requiring improvement.

### Misconceptions

Only misconceptions actually observed during the interview.

### Competency Breakdown

Example:

```text
Conceptual Understanding     86%
Practical Application        78%
Engineering Reasoning        72%
System Design                65%
Communication                88%
```

### Curriculum Coverage

Topics and curriculum days evaluated during the interview.

### Evidence

Concise observations supporting the assessment.

### Recommendations

Specific concepts and skills to revise.

---

# Personalized 7-Day Learning Path

The system converts observed weaknesses into an actionable revision plan.

Example:

```text
Day 1
Retrieval fundamentals

Day 2
Chunking strategies

Day 3
Vector search optimization

Day 4
Hybrid retrieval

Day 5
RAG evaluation

Day 6
Production RAG architecture

Day 7
Senior-level RAG mock interview
```

Recommendations are grounded in the available curriculum rather than generic AI advice.

---

# Interview Fingerprint

The final report generates a compact technical profile.

```text
TECHNICAL INTERVIEW FINGERPRINT

Conceptual Knowledge       89%
Practical Application      77%
Engineering Reasoning      71%
System Design              64%
Communication              86%

Overall Readiness          79%

Primary Strength:
Technical communication

Primary Gap:
Architecture trade-offs

Best Improvement Area:
Production system design
```

---

# API Documentation

The API contract follows the requirements defined in `technical-specs.md`.

## `POST /api/interview`

Starts or continues an interview session according to the API contract.

### Start Interview

```json
{
  "sessionId": "abc-123",
  "candidate": {}
}
```

### Continue Interview

```json
{
  "sessionId": "abc-123",
  "message": "My answer here..."
}
```

### In-Progress Response

```json
{
  "reply": "Next question text...",
  "done": false
}
```

### Completed Response

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

> **Note:** The exact request and response schemas defined in `technical-specs.md` take precedence over these illustrative examples.

---

## `GET /health`

Returns service status and RAG readiness.

Example:

```json
{
  "status": "healthy",
  "ragReady": true
}
```

---

# Setup

## 1. Clone the Repository

```bash
git clone <repository-url>
cd interview-agent-backend
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Copy the example environment file:

### Windows

```bash
copy .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Then configure the required variables.

---

# Environment Variables

| Variable              | Required | Default                     | Description                     |
| --------------------- | -------- | --------------------------- | ------------------------------- |
| `OPENAI_API_KEY`      | Yes      | —                           | OpenAI or compatible API key    |
| `OPENAI_BASE_URL`     | No       | `https://api.openai.com/v1` | API base URL                    |
| `OPENAI_MODEL`        | No       | `gpt-4o-mini`               | Main generation model           |
| `EVAL_MODEL`          | No       | `gpt-4o-mini`               | Evaluation model                |
| `APP_ENV`             | No       | `development`               | Application environment         |
| `LOG_LEVEL`           | No       | `INFO`                      | Logging level                   |
| `MAX_QUESTIONS`       | No       | `10`                        | Interview upper limit           |
| `MIN_QUESTIONS`       | No       | `8`                         | Minimum interview questions     |
| `MIN_CURRICULUM_DAYS` | No       | `4`                         | Minimum curriculum-day coverage |

---

# Running Locally

Start the development server:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at:

```text
http://localhost:8000
```

FastAPI interactive documentation:

```text
http://localhost:8000/docs
```

---

# Production

Run the application with:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

# Testing

Run all tests:

```bash
pytest tests/ -v
```

Run tests with coverage:

```bash
pytest tests/ --cov=app --cov-report=html
```

---

# Deployment

## Render

Render is recommended for the FastAPI backend.

### Steps

1. Push the repository to GitHub.
2. Create a new Web Service on Render.
3. Connect the repository.
4. Configure the required environment variables.
5. Deploy the service.

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

A `render.yaml` configuration can also be provided for automated deployment.

---

## Vercel

Vercel is primarily optimized for serverless applications and frontend deployments.

For this stateful FastAPI backend, **Render, Railway, or Fly.io** are recommended.

If Vercel is used, an appropriate serverless adapter must be configured.

---

## Docker

Build the image:

```bash
docker build -t interview-agent .
```

Run the container:

```bash
docker run -p 8000:8000 --env-file .env interview-agent
```

---

# Project Structure

```text
interview-agent-backend/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── api/
│   │   └── interview.py
│   │
│   ├── agents/
│   │   ├── interview_agent.py
│   │   ├── strategy_engine.py
│   │   └── question_planner.py
│   │
│   ├── evaluation/
│   │   ├── answer_evaluator.py
│   │   ├── competency_engine.py
│   │   └── contradiction_detector.py
│   │
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── ingestion.py
│   │   └── retriever.py
│   │
│   ├── memory/
│   │   └── interview_memory.py
│   │
│   ├── services/
│   │   ├── curriculum_service.py
│   │   ├── candidate_service.py
│   │   ├── interview_service.py
│   │   └── feedback_service.py
│   │
│   ├── prompts/
│   │   ├── interviewer.py
│   │   ├── evaluator.py
│   │   ├── planner.py
│   │   ├── grounding.py
│   │   └── feedback.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   └── core/
│       ├── config.py
│       └── logging.py
│
├── data/
│   ├── curriculum.json
│   └── candidates.json
│
├── tests/
│
├── deploy/
│   └── render.yaml
│
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── PROMPTS.md
```

---

# Design Decisions

## FAISS over Chroma/Pinecone

FAISS provides:

- Fast similarity search
- No external database dependency
- Simple deployment
- Sufficient performance for the 31-day curriculum

For this hackathon, the curriculum is small enough that a lightweight vector index is preferable to introducing unnecessary infrastructure.

---

## Single Backend Service

The project uses a single FastAPI service rather than unnecessary microservices.

This keeps:

- development fast
- deployment simple
- debugging easier
- the architecture understandable

The internal modules remain separated so individual components can later be extracted if needed.

---

## OpenAI-Compatible API

The LLM integration uses an OpenAI-compatible interface so the underlying model provider can be changed without rewriting the interview engine.

---

## In-Memory Session Store

Interview sessions are stored in memory for the hackathon.

This is sufficient because:

- persistent user accounts are out of scope
- long-term conversation history is not required
- the evaluation focuses on the interview experience

For production, the session layer can be replaced with Redis or another persistent store.

---

## Structured LLM Outputs

Evaluation and planning outputs use structured schemas rather than relying on free-form model responses.

This improves:

- reliability
- parsing
- validation
- frontend integration
- deterministic decision-making

---

## Deterministic + LLM Hybrid

The system combines deterministic software logic with LLM reasoning.

### Deterministic logic handles:

- session state
- question counts
- curriculum coverage
- duplicate detection
- interview termination
- score aggregation
- API validation

### LLM handles:

- question generation
- answer interpretation
- technical evaluation
- semantic reasoning
- feedback generation
- natural conversational responses

This prevents the application from becoming an uncontrolled LLM wrapper.

---

# Limitations

- Session state is currently stored in memory and is lost if the server restarts.
- The FAISS index is rebuilt during application startup.
- Contradiction detection is intentionally conservative to minimize false positives.
- The system depends on an external LLM API.
- LLM inference introduces latency and API costs.

---

# Future Improvements

Potential production improvements include:

- Redis-backed session persistence
- Persistent FAISS indexes
- Incremental curriculum indexing
- More advanced semantic contradiction detection
- Voice-based interviews
- Real-time interviewer dashboards
- Multi-language technical interviews
- Interview analytics
- Historical candidate benchmarking
- A/B testing of interview strategies
- Integration with recruitment platforms

---

# AI Usage & Development Transparency

The project includes `PROMPTS.md`, documenting the major AI prompts used during development.

This includes prompts for:

- Interview strategy generation
- Question planning
- Question generation
- Answer evaluation
- Competency analysis
- Contradiction detection
- Curriculum grounding
- Final feedback generation

The repository maintains an authentic development history reflecting the actual implementation process.

---

# Project Goals

The system is designed around five principles:

### 1. Personalized

The interview changes according to the candidate's learning journey.

### 2. Adaptive

The next question depends on the candidate's previous response.

### 3. Grounded

Questions are based on the actual curriculum.

### 4. Evidence-Driven

Assessment is supported by observed candidate behavior.

### 5. Human-Like

The interviewer probes, challenges, redirects, and adapts instead of following a script.

---

# The Core Idea

Traditional AI Interviewer:

```text
Question
   ↓
Answer
   ↓
Next Question
   ↓
Answer
```

Interview Intelligence Engine:

```text
Candidate Evidence
        ↓
Interview Strategy
        ↓
Curriculum Retrieval
        ↓
Question
        ↓
Candidate Answer
        ↓
Deep Evaluation
        ↓
Competency Update
        ↓
Memory + Contradiction Check
        ↓
Strategy Replanning
        ↓
Adaptive Follow-up
        ↓
Deeper Assessment
        ↓
Evidence-Based Feedback
```

---

# Why It Is Different

> **Most AI interviewers generate questions.**
>
> **Interview Intelligence Engine builds an interview strategy.**

It does not simply ask whether a candidate knows a concept.

It investigates whether they can:

- explain it
- apply it
- debug it
- reason about it
- evaluate trade-offs
- design systems around it
- communicate their engineering decisions

### The goal is not to measure memorization.

### The goal is to measure engineering understanding.

---

# License

This project was created for the **ABTalks AI Cohort hackathon** and uses synthetic curriculum and candidate data provided for the challenge.
