# AI-Powered Intelligent Query Resolution System

A domain-agnostic, voice-and-text-enabled conversational platform. Upload any knowledge base (HR policies, manuals, FAQs, student handbooks) and query it instantly through natural language using a multi-agent RAG pipeline.

---

## 🏗️ Architecture

```
User (Browser)
   ↕ HTTP/REST
Frontend (React + Vite) — Login, Upload, Chat, History, Dashboard
   ↕ Axios API calls
Backend (FastAPI)
   ├─ Auth Module (JWT access + refresh tokens)
   ├─ API Gateway (/auth, /upload, /query, /history, /analytics)
   ├─ Business Services (query, history, analytics, upload, user)
   ├─ Agent Orchestrator (LangGraph — 5 agents)
   │     ├─ Query Understanding Agent
   │     ├─ Clarification Agent (ambiguous queries)
   │     ├─ Retrieval Agent (ChromaDB semantic search)
   │     ├─ Response Generation Agent (Ollama LLM)
   │     └─ Memory Agent (PostgreSQL persistence)
   └─ RAG Pipeline (PDF/DOCX/TXT/CSV → Chunks → Embeddings → ChromaDB)
        ↕
   Data Layer: PostgreSQL (relational) + ChromaDB (vectors)
        ↕
   Local LLM: Ollama (llama3.2:1b for chat, nomic-embed-text for embeddings)
```

### Confidence Score Formula
```
overall_confidence = (retrieval_confidence + generation_confidence) / 2.0

High   > 0.80
Medium > 0.50
Low    ≤ 0.50
```

---

## ⚙️ Requirements

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.11+ | |
| Node.js | 18+ | |
| PostgreSQL | 14+ | Version 18 also works |
| Ollama | 0.3+ | For local LLM |
| Chrome / Edge | Latest | Required for Voice (Web Speech API) |

> **Note:** This project is optimized for lightweight hardware (Intel i3, 8 GB RAM).
> It uses `llama3.2:1b` (1.3 GB) for chat and `nomic-embed-text` (274 MB) for embeddings.

---

## 🚀 Local Setup

### 1. Clone & Install

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Install & Start Ollama

Download Ollama from https://ollama.com/download

```bash
# Pull the required models
ollama pull llama3.2:1b
ollama pull nomic-embed-text

# Ollama runs automatically as a service on Windows
# Verify it's working:
ollama list
```

### 3. Set Up PostgreSQL

Create a database and user in pgAdmin 4 or psql:

```sql
CREATE USER qrs_user WITH PASSWORD 'qrs_password123';
CREATE DATABASE qrs_db OWNER qrs_user;
```

### 4. Configure Environment

Create `backend/.env` with the following content:

```env
# Database
SQLALCHEMY_DATABASE_URL=postgresql://qrs_user:qrs_password123@localhost:5432/qrs_db

# JWT
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_CHAT_MODEL=llama3.2:1b
OLLAMA_EMBED_MODEL=nomic-embed-text

# RAG Parameters
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K=5
SIMILARITY_THRESHOLD=0.5
CHROMA_PERSIST_DIR=./chroma_db
```

### 5. Start the Application

**Terminal 1 — Backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open your browser at: **http://localhost:5173**

---

## 📖 Usage

1. **Register / Login** at `/login`
2. **Upload documents** at `/upload` (PDF, DOCX, TXT, or CSV)
3. **Ask questions** at `/chat` — type or use the 🎤 mic button
4. **View history** at `/history` — browse and reload past sessions
5. **Analytics** at `/dashboard` — track usage and knowledge gaps

### Voice Features (Chrome/Edge only)
- Click 🎤 to speak your question — text appears in real-time
- Click 🔊/🔇 to toggle auto-read of AI responses
- If the mic doesn't work: click the lock icon in the URL bar and set Microphone to "Allow"

---

## 🤖 The 5 Agents

| Agent | Role |
|-------|------|
| **Query Understanding** | Classifies query as `factual`, `procedural`, `comparative`, or `ambiguous` |
| **Clarification** | For ambiguous queries, asks a targeted follow-up question |
| **Retrieval** | Semantic search across ChromaDB, returns top-K chunks with similarity scores |
| **Response Generation** | Synthesizes a grounded answer from retrieved chunks only |
| **Memory** | Saves all messages to PostgreSQL, enables multi-turn context |

---

## 🌍 Domain-Agnostic Usage

The system works with any knowledge domain — no code changes needed. Just upload new documents:
- HR Policies & Employee Handbooks
- Technical Documentation
- Student Handbooks
- Product FAQs
- Medical Guidelines
- Legal Documents

---

## 📁 Project Structure

```
/frontend/src
  /pages       — Login, Register, Upload, Chat, History, Dashboard
  /components  — ChatBubble, SourcePanel, ConfidenceBadge, VoiceButton, AnalyticsCharts
  /hooks       — useSpeechRecognition, useSpeechSynthesis
  /api         — axios wrappers for all API endpoints
  /store       — Zustand auth store

/backend/app
  /api         — FastAPI routers (auth, upload, query, history, analytics)
  /services    — Business logic layer
  /agents      — 5 LangGraph agents + orchestrator
  /rag         — Document loader, chunker, embeddings, vector store, retriever
  /models      — SQLAlchemy ORM models
  /schemas     — Pydantic request/response schemas
  /core        — Config, security (JWT), database session
```

---

## 🔧 Tuning Parameters

All configurable via `backend/.env`:

| Parameter | Default | Effect |
|-----------|---------|--------|
| `CHUNK_SIZE` | 500 | Larger = more context per chunk, but slower |
| `CHUNK_OVERLAP` | 50 | Prevents losing context at chunk boundaries |
| `TOP_K` | 5 | Number of chunks retrieved per query |
| `SIMILARITY_THRESHOLD` | 0.5 | Minimum relevance score (0-1). Higher = stricter |

---

## ⚠️ Known Constraints

- **Voice** only works in Chrome and Edge (Web Speech API requirement).
- `llama3.2:1b` is optimized for low-RAM machines. Larger models (e.g., `llama3.1:8b`) would give better answers but require 8 GB+ VRAM.
- ChromaDB telemetry errors in the console are harmless and can be ignored.
