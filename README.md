# AI-Powered Intelligent Query Resolution System

An end-to-end web application that allows users to upload knowledge bases (PDF, DOCX, TXT, CSV) and query them instantly through natural language using a multi-agent RAG (Retrieval-Augmented Generation) pipeline.

## Features

- **Document Ingestion**: Upload documents, chunk text, and embed into ChromaDB.
- **RAG Pipeline**: Advanced multi-agent LangGraph workflow.
- **Local LLM**: Powered by Ollama for privacy and offline capabilities.
- **Modern UI**: React and Vite frontend with a dark-mode inspired design system.

## Setup Instructions

### Prerequisites
- [Docker](https://www.docker.com/get-started) and Docker Compose
- [Ollama](https://ollama.com/) (Optional if using the dockerized Ollama, but recommended for local model management)

### 1. Environment Variables

Create a `.env` file in the `backend/` directory based on `backend/.env.example`.
Key variables include:
- `OLLAMA_BASE_URL`: Usually `http://localhost:11434` or `http://ollama:11434` if running in Docker.
- `OLLAMA_CHAT_MODEL`: E.g., `llama3.1`
- `OLLAMA_EMBED_MODEL`: E.g., `nomic-embed-text`
- `CHROMA_MODE`: Set to `local` for SQLite-backed Chroma, or `http` for a standalone Chroma server.

### 2. Pulling Ollama Models

Before starting the backend, make sure Ollama has the required models pulled. If using the dockerized Ollama, you can pull models via the container:
```bash
docker-compose exec ollama ollama run nomic-embed-text
docker-compose exec ollama ollama run llama3.1
```
(Press Ctrl+D after the model finishes downloading and you see the prompt).

### 3. Running with Docker Compose

To spin up the entire stack (Frontend, Backend, Chroma, Ollama):
```bash
docker-compose up --build
```

- **Frontend**: Available at http://localhost:5173
- **Backend API**: Available at http://localhost:8000
- **API Docs (Swagger)**: Available at http://localhost:8000/docs

### 4. End-to-End Demo
1. Open the frontend at `http://localhost:5173`.
2. Register a new user and log in.
3. Navigate to the Upload section and drop a sample PDF or TXT file.
4. Wait for the file to be processed (chunked and embedded).
5. (Upcoming) Go to Chat and ask a query based on the uploaded document.
