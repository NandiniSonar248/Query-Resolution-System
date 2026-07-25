# MASTER BUILD PROMPT — AI-Powered Intelligent Query Resolution System

> Copy everything below into Antigravity as a single project brief. It is self-contained: architecture, tech stack, folder layout, agent contracts, workflow logic, and phased milestones are all included so the agent can plan and build without needing you to re-explain context mid-build.

---

## 1. ROLE & OBJECTIVE

You are acting as a senior full-stack AI engineer. Build a complete, working, end-to-end web application called the **AI-Powered Intelligent Query Resolution System** — a domain-agnostic, voice-and-text-enabled conversational platform that lets any user upload a knowledge base (policies, manuals, FAQs, handbooks — any domain) and query it instantly through natural language, with a multi-agent RAG pipeline resolving each query and full source transparency shown to the user.

This must be a genuinely working, runnable application — not a mockup. Every module below must be implemented with real logic (real embeddings, real vector search, real agent orchestration), not stubbed or hardcoded responses. Where a component has multiple valid implementations, pick the most standard, well-documented option and proceed — don't stop to ask me unless something is truly blocking (e.g., a missing credential).

---

## 2. TECH STACK (fixed — do not substitute without telling me why)

**Frontend:** React + Vite

- Pages/panels: Login/Register, Upload Documents, Chat Interface, Dashboard & Analytics, History
- Voice: browser-native **Web Speech API** (SpeechRecognition for input, SpeechSynthesis for text-to-speech output) — no external voice API/service.

**Backend:** FastAPI (Python), REST API over HTTPS, JSON.

**Backend internal layers:**

- **Auth Module** — Register, Login, JWT access token, refresh token, token rotation, logout.
- **API Gateway layer** — Auth APIs, Upload APIs, Query APIs, History APIs, Analytics APIs, User APIs.
- **Business Services** — Upload Service, Query Service, History Service, Analytics Service, User Service.
- **Agent Orchestrator** — built with **LangGraph** (multi-agent graph/state machine layer). This is the core orchestration engine coordinating all 5 agents per query.
- **RAG Pipeline** — Document Loader (PDF, DOCX, TXT, CSV) → Text Chunking → Embeddings Generator → Vector Store (ChromaDB) → Retriever (top-K chunks).

**Data layer:**

- **Relational DB:** PostgreSQL (or SQLite for local/dev) — stores Users, Documents metadata, Chat Sessions, Messages, Analytics, Knowledge Gap Logs.
- **Vector DB:** ChromaDB — stores document embeddings and chunk embeddings.

**LLM layer:** Local LLM via **Ollama** (e.g. Llama 3.1 / Mistral / Gemma for generation, `nomic-embed-text` or similar for embeddings). Design the LLM/embedding calls behind an interface so a cloud provider (OpenAI/Anthropic API) can be swapped in later without touching agent logic.

**External services (optional/future, stub as pluggable interfaces only, not required for MVP):** SMTP email service, Whisper STT, Coqui/Piper TTS. Do NOT build these now — just leave clean extension points.

---

## 3. SYSTEM ARCHITECTURE (as designed — follow exactly)

```
User (HR / Team / Employee)
   ↕ HTTPS/REST
Frontend (React+Vite): Login/Register | Upload Documents | Chat Interface | Dashboard & Analytics | History
   ↕ HTTPS/REST
Backend (FastAPI)
  ├─ Auth Module
  ├─ API Gateway (Auth/Upload/Query/History/Analytics/User APIs)
  ├─ Business Services (Upload/Query/History/Analytics/User Service)
  ├─ Agent Orchestrator (LangGraph) — runs the 5 agents per query in sequence/graph
  └─ Feature Modules — Response Transparency, Conversation Memory, Query Analytics & Dashboard, Knowledge Gap Detection
        ↕
  RAG Pipeline: Document Loader → Text Chunking → Embeddings Generator → Vector Store (ChromaDB) → Retriever (Top-K)
        ↕
  Data Layer: PostgreSQL/SQLite (relational) + ChromaDB (vector)
        ↕
  Local LLM Layer (Ollama: generation model + embedding model)
```

**Per-query workflow (this is the exact control flow to implement in LangGraph):**

1. User asks a question (text or voice → transcribed to text).
2. **Query Understanding Agent** classifies query intent/type: `factual | procedural | comparative | ambiguous`.
3. Branch on query type:
   - `factual` / `procedural` / `comparative` → straight to **Retrieval Agent** (semantic search in vector DB).
   - `ambiguous` → **Clarification Agent** asks a targeted follow-up question, waits for user's clarifying reply, then loops back into the flow with the enriched query → Retrieval Agent.
4. **Retrieval Agent** performs semantic search, returns top-K relevant chunks with relevance/similarity scores, filters out low-confidence chunks.
5. **Response Generation Agent** synthesizes a grounded answer strictly from retrieved chunks, attaching source citations.
6. **Confidence Scoring & Source Attribution** step computes an overall confidence score for the answer (based on retrieval similarity + generation grounding) and attaches source chunk references.
7. **Memory Agent** updates the multi-turn conversation context/state for this session.
8. Final response returned to user: **Answer + Sources + Confidence score**, rendered in chat and (if voice mode) spoken aloud via SpeechSynthesis while text displays simultaneously.

Implement this exact graph in LangGraph with explicit nodes for each agent and a conditional edge on query type (this maps directly to your workflow diagram — Query Understanding → decision diamond → Factual/Procedural/Comparative/Ambiguous branches → Retrieval/Clarification → Response Generation → Confidence Scoring → Memory Agent → Final Response).

---

## 4. AGENT SPECIFICATIONS (implement all 5 as distinct LangGraph nodes with clear input/output contracts)

### 4.1 Query Understanding Agent

- **Input:** raw user query (+ prior conversation context from Memory Agent).
- **Logic:** LLM-based classification into one of: `factual`, `procedural`, `comparative`, `ambiguous`. Also extract a normalized/rewritten query (resolving pronouns/references using conversation history, e.g. "what about the second one" → resolved query).
- **Output:** `{ query_type, normalized_query, confidence }`.

### 4.2 Retrieval Agent

- **Input:** normalized query.
- **Logic:** embed the query with the same embedding model used for ingestion → semantic search against ChromaDB → retrieve top-K (configurable, default K=5) → rank by similarity score → filter chunks below a minimum similarity threshold (configurable, default 0.5–0.6 depending on embedding model).
- **Output:** `{ chunks: [{text, source_doc, page/section, similarity_score}], retrieval_confidence }`.

### 4.3 Response Generation Agent

- **Input:** normalized query + retrieved chunks + conversation history.
- **Logic:** LLM prompt strictly instructed to answer only from provided chunks, cite which chunk(s) each claim comes from, and explicitly say "I don't have enough information" when chunks don't support an answer (no hallucination beyond retrieved context).
- **Output:** `{ answer_text, citations: [{chunk_id, source_doc}], generation_confidence }`.

### 4.4 Clarification Agent

- **Input:** query flagged `ambiguous` (or multi-part) by Query Understanding Agent.
- **Logic:** LLM generates 1 targeted clarifying question (not generic "can you elaborate" — must reference the specific ambiguity, e.g. multiple entities/time periods/documents that could match). On user's reply, merges clarification into the original query and re-routes into the main flow.
- **Output:** `{ clarifying_question }` → then on reply → `{ resolved_query }`.

### 4.5 Conversation Memory Agent

- **Input:** every turn's query, agent decisions, and response.
- **Logic:** maintains a per-session rolling context (last N turns, or summarized context beyond a token budget) so follow-up queries work without the user re-stating context. Persist session + messages to the relational DB.
- **Output:** updated session state; also exposes conversation history for the History module/UI.

**Confidence score displayed to user** = a combined score derived from `retrieval_confidence` and `generation_confidence` (define and document your exact formula, e.g. weighted average), shown as a percentage or High/Medium/Low badge next to every answer.

---

## 5. FEATURE MODULES (build all — these are explicit deliverables, not optional polish)

1. **Knowledge Base Ingestion & RAG Pipeline** — multi-format upload (PDF, DOCX, TXT, FAQ CSV), chunking (with configurable chunk size/overlap), embedding generation, vector store indexing, ingestion status feedback in UI.
2. **Multi-Agent Orchestration & Query Routing Layer** — the LangGraph graph described in Section 3.
3. **Voice Input & Text-to-Speech Response** — Web Speech API integration: mic button starts SpeechRecognition, transcript populates the chat input, response is read aloud via SpeechSynthesis with simultaneous text display. Handle browser support gracefully (feature-detect; fall back to text-only with a visible notice if unsupported).
4. **Conversational Interface with Multi-Turn Memory** — chat UI showing full turn history, clarification exchanges rendered distinctly from normal Q&A turns.
5. **Response Transparency Panel** — per answer, an expandable panel showing: retrieved source chunks (with document name + excerpt), citation markers inline in the answer, confidence score/badge.
6. **Query Analytics & Knowledge Gap Detection Dashboard** — tracks: query volume trends over time, top/most frequent queries, queries with low confidence or no answer ("unanswered queries" log), inferred knowledge gaps (topics repeatedly asked about but poorly answered) — rendered as charts + tables on the Dashboard.

---

## 6. DATA MODELS (design these tables/collections — adjust field names as needed but cover this data)

**Relational DB:**

- `users` (id, name, email, hashed_password, role, created_at)
- `documents` (id, user_id, filename, file_type, upload_date, chunk_count, status)
- `chat_sessions` (id, user_id, created_at, title)
- `messages` (id, session_id, role[user/assistant/clarification], content, query_type, confidence_score, citations_json, created_at)
- `knowledge_gap_logs` (id, query_text, query_type, confidence_score, was_answered, created_at)

**Vector DB (ChromaDB collections):**

- `document_chunks` — vectors + metadata (`document_id`, `source_doc_name`, `chunk_index`, `raw_text`, `page/section`)

---

## 7. NON-FUNCTIONAL REQUIREMENTS

- JWT-based auth with access + refresh tokens and token rotation on refresh; protect all API routes except register/login.
- CORS configured for the Vite dev server origin.
- Environment-based config (`.env`) for DB URL, Ollama host/model names, JWT secret, chunk size, top-K, similarity threshold — nothing hardcoded.
- Structured error handling and meaningful HTTP status codes across all API endpoints.
- Basic input validation (file type/size limits on upload, query length limits).
- Dockerize both frontend and backend (Dockerfile each) plus a `docker-compose.yml` that also spins up Ollama and (if using Postgres) the DB container, so the whole system runs with one command.
- Include a `README.md` with setup steps, environment variables, how to pull Ollama models, and how to run the demo end-to-end.

---

## 8. FOLDER STRUCTURE (use this as the baseline)

```
/frontend
  /src
    /pages          (Login, Register, Upload, Chat, Dashboard, History)
    /components      (ChatBubble, SourcePanel, ConfidenceBadge, VoiceButton, UploadDropzone, AnalyticsCharts)
    /hooks           (useSpeechRecognition, useSpeechSynthesis, useAuth, useChat)
    /api             (axios/fetch client wrappers per API Gateway group)
    /store           (session/auth state)
/backend
  /app
    /api             (routers: auth.py, upload.py, query.py, history.py, analytics.py, user.py)
    /services        (upload_service.py, query_service.py, history_service.py, analytics_service.py, user_service.py)
    /agents          (query_understanding.py, retrieval.py, response_generation.py, clarification.py, memory.py, orchestrator.py [LangGraph graph def])
    /rag             (loader.py, chunker.py, embeddings.py, vector_store.py, retriever.py)
    /models          (SQLAlchemy models)
    /schemas         (Pydantic request/response schemas)
    /core            (config.py, security.py/JWT, db.py)
  main.py
  requirements.txt
docker-compose.yml
README.md
```

---

## 9. BUILD PLAN — implement in this exact phased order (mirrors the project's official milestones; treat each phase as a checkpoint and confirm it runs before moving to the next)

**Phase 1 — Foundations & Ingestion**

- Scaffold FastAPI backend + React/Vite frontend, Docker setup, Postgres/SQLite + ChromaDB wired up.
- Auth module (register/login/JWT/refresh) end-to-end, working login UI.
- Knowledge Base Ingestion Module: upload PDF/DOCX/TXT/CSV → chunk → embed (Ollama embedding model) → store in ChromaDB, with metadata linking chunks to documents.
- Validate retrieval quality manually against 2 different sample knowledge bases you generate for testing (e.g. a fake HR policy doc and a fake product FAQ).

**Phase 2 — Core Agent Pipeline**

- Query Understanding Agent (classification + query normalization).
- Retrieval Agent (semantic search, ranking, filtering).
- Response Generation Agent (grounded answer + citations + confidence).
- LangGraph orchestrator wiring these 3 together sequentially, exposed via a `/query` API endpoint. Working chat UI hitting this endpoint.

**Phase 3 — Clarification, Memory, Voice, Transparency**

- Clarification Agent + branch logic for ambiguous queries in the LangGraph graph.
- Conversation Memory Agent — multi-turn context, session persistence, History page working.
- Web Speech API voice input + TTS output wired into the Chat UI.
- Response Transparency Panel — source chunks, relevance scores, citations rendered per answer.

**Phase 4 — Analytics, Testing, Polish**

- Query Analytics & Knowledge Gap Detection module + Dashboard UI (charts for trends, top queries, low-confidence/unanswered logs).
- End-to-end test pass across at least 3 distinct knowledge base domains (e.g. HR policy, technical documentation, student handbook) — verify retrieval accuracy, agent routing correctness, voice interaction, and multi-turn memory all work.
- Tune chunk size, top-K, similarity threshold, and prompts based on test results.
- Finalize README, architecture notes, and a short demo script showing the system working across multiple domains.

At the end of each phase, run the app and confirm it's actually working (real upload → real retrieval → real generated answer with real citations) before proceeding — don't stack unverified phases.

---

## 10. ACCEPTANCE CRITERIA (this is how the finished system will be judged — build to satisfy these explicitly)

- [ ] Retrieval and generated answers are accurate and relevant across varied uploaded knowledge domains (test with ≥3 domains).
- [ ] All 5 agents visibly collaborate per query: classification → routing → retrieval/clarification → generation → memory update — this should be traceable (e.g. via logs or a debug view) not just a black box.
- [ ] Voice input and TTS output work reliably in a modern browser (Chrome/Edge).
- [ ] Every answer displays source chunks, a confidence score, and citations — no answer without transparency.
- [ ] Ambiguous queries correctly trigger the Clarification Agent and resolve after user reply.
- [ ] Multi-turn follow-up queries correctly use prior context without the user restating it.
- [ ] Knowledge Gap Detection dashboard correctly surfaces unanswered/low-confidence queries and query trends.
- [ ] System is domain-agnostic: swapping the uploaded knowledge base (e.g. from HR policy to technical docs) requires no code changes.
- [ ] Fully runnable via `docker-compose up` (or clearly documented local setup) with a working README.

---

## 11. WHAT TO DO IF SOMETHING IS AMBIGUOUS

Where this brief doesn't specify an exact value (e.g. exact chunk size, exact confidence formula, exact UI styling), choose sensible, well-justified defaults, document the choice briefly in the README or code comments, and keep going — don't block progress waiting for clarification unless it's a genuine blocker (missing API key/model you can't install, etc.).

Now begin with Phase 1.
