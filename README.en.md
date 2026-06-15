# SmartSweepAgent · Robot Vacuum AI Customer-Service Agent

An AI customer-service Agent for the robot vacuum domain, built with **LangChain + FastAPI**. It supports RAG knowledge-base Q&A, multi-turn conversation, user authentication with session isolation, caching, and rate limiting — a complete backend-engineered AI application.

> 中文文档见 [README.md](README.md)

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Running Tests](#running-tests)
- [FAQ](#faq)

---

## Features

| Module | Description |
| --- | --- |
| **ReAct Agent** | Built on LangChain with tool calling (knowledge retrieval, weather, user info, external data, report generation), plus middleware for tool monitoring and dynamic prompt switching |
| **RAG Knowledge Base** | Chroma vector retrieval + Reranker re-ranking: recall Top-K candidates, then re-rank to keep Top-N, improving answer relevance |
| **Multi-turn Chat** | Sessions persisted in SQLite, so history survives service restarts |
| **User System** | JWT authentication + bcrypt password hashing, per-user session isolation, with anonymous access supported |
| **Cache / Rate Limit** | Redis caches RAG retrieval results and rate-limits by IP+path; degrades gracefully when Redis is unavailable, keeping core features working |
| **Unified Response** | All endpoints return a standard `{code, message, data, request_id, elapsed_ms}` structure, with global exception handling and request tracing |
| **Dual Entry Points** | FastAPI provides a standard REST API; a Streamlit page is kept for quick demos |

---

## Tech Stack

- **Web Framework**: FastAPI · Uvicorn · Pydantic
- **LLM / Agent**: LangChain · LangGraph · Tongyi Qianwen (qwen3-max)
- **RAG**: Chroma · DashScope Embeddings (text-embedding-v4)
- **Database**: SQLAlchemy + SQLite
- **Cache / Rate Limit**: Redis
- **Auth**: python-jose (JWT) · passlib + bcrypt
- **Demo Frontend**: Streamlit

---

## Architecture

```
                    HTTP Request
                        │
        ┌───────────────▼────────────────┐
        │  Middleware: request ID / timing / access log │
        └───────────────┬────────────────┘
                        │
                ┌───────▼────────┐
                │  Rate limit (Redis) │
                └───────┬────────┘
                        │
              ┌─────────▼──────────┐
              │  API Router Layer   │  api/routers
              │  auth / chat / health│
              └─────────┬──────────┘
                        │
         ┌──────────────┼───────────────┐
         │              │               │
  ┌──────▼─────┐ ┌──────▼──────┐ ┌──────▼───────┐
  │ ReactAgent │ │SessionManager│ │  RAG Service  │
  │ + tools    │ │ + Repository │ │ retrieve+rerank+cache │
  └──────┬─────┘ └──────┬──────┘ └──────┬───────┘
         │              │               │
   tool/model calls   SQLite persist  Chroma + Redis
```

Request flow: middleware injects request context → rate-limit check → route dispatch → business layer (Agent / session management / RAG) → data layer (SQLite / Chroma) → unified response.

---

## Project Structure

```
SmartSweepAgent/
├── api/                   # FastAPI service layer
│   ├── main.py               # App entry: router registration, middleware, global exception handling
│   ├── context.py            # Request-scoped ContextVar (request ID, start time)
│   ├── routers/              # Routes: auth / chat / health
│   ├── schemas/              # Pydantic request/response models
│   ├── dependencies/         # Dependency injection: auth (JWT) / rate_limit
│   ├── middleware/           # HTTP middleware: access logging
│   └── exceptions/           # Business exception definitions
├── agent/                 # Agent
│   ├── react_agent.py        # ReAct Agent wrapper
│   └── tools/                # Tool definitions and Agent middleware
├── rag/                   # Retrieval-augmented generation
│   ├── vector_store.py       # Chroma vector store (build / retrieve)
│   ├── retriever.py          # Hybrid retriever (retrieve + rerank)
│   ├── reranker.py           # Re-ranking
│   └── rag_service.py        # RAG main flow (with cache)
├── session/               # Sessions and users
│   ├── models.py             # SQLAlchemy ORM (users / sessions / messages)
│   ├── repository.py         # Database CRUD
│   └── session_manager.py    # Business management layer
├── model/
│   └── factory.py            # Model factory (Chat / Embedding)
├── utils/                 # Shared utilities
│   ├── config_handler.py     # YAML config loading
│   ├── db.py                 # Database connection and sessions
│   ├── redis_client.py       # Redis connection (with degradation)
│   ├── cache.py              # Cache read/write wrapper
│   ├── jwt_handler.py        # JWT encode/decode
│   ├── logger_handler.py     # Logging
│   ├── file_handler.py       # File loading and MD5
│   ├── prompt_loader.py      # Prompt loading
│   └── path_tool.py          # Path utilities
├── config/                # YAML config files
│   ├── agent.yml / chroma.yml / rag.yml / prompts.yml
│   ├── redis.yml / auth.yml
├── prompts/                  # Prompt text
├── data/                     # Knowledge-base source files and SQLite database
├── logs/                     # Runtime logs
├── app.py                    # Streamlit demo entry
├── requirements.txt
└── README.md
```

---

## Requirements

- Python 3.10+ (developed on 3.11)
- Redis (optional; degrades automatically when not running — caching and rate limiting are disabled but chat still works)
- Tongyi Qianwen / DashScope API Key

---

## Quick Start

### 1. Create a virtual environment and install dependencies

```bash
conda create -n RAG_Agent python=3.11
conda activate RAG_Agent
pip install -r requirements.txt
```

### 2. Configure the API Key

The project uses the Tongyi Qianwen model and requires the DashScope API Key environment variable:

```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY="your-key"

# Linux / macOS
export DASHSCOPE_API_KEY="your-key"
```

### 3. Review config files

Adjust the files under `config/` as needed (see [Configuration](#configuration)).
**In production, be sure to change `secret_key` in `config/auth.yml` and safeguard the password in `config/redis.yml`.**

### 4. Build the knowledge base (first run)

Put your knowledge documents into the `data/` directory (`.txt` / `.pdf` supported), then build the vector store:

```bash
python -m rag.vector_store
```

> Deduplicated by file MD5, so re-running won't ingest duplicates.

### 5. Start the API server

```bash
python -m uvicorn api.main:app --port 8000
```

After startup, open the interactive docs at `http://127.0.0.1:8000/docs`

### 6. (Optional) Start the Streamlit demo

```bash
streamlit run app.py
```

---

## Configuration

All configuration lives in the `config/` directory, in YAML format.

| File | Key | Description |
| --- | --- | --- |
| `rag.yml` | `chat_model_name` / `embedding_model_name` | Chat model and embedding model names |
| `chroma.yml` | `retriever_k` / `rerank_top_k` | Vector recall count / kept count after re-ranking |
| `chroma.yml` | `chunk_size` / `chunk_overlap` | Document chunk size and overlap |
| `chroma.yml` | `data_path` / `persist_directory` | Knowledge source directory / vector store persistence directory |
| `agent.yml` | `external_data_path` | External user data file path |
| `prompts.yml` | `*_prompt_path` | Prompt file paths per scenario |
| `redis.yml` | `host` / `port` / `password` | Redis connection info |
| `redis.yml` | `cache.rag_ttl` | RAG cache TTL (seconds) |
| `redis.yml` | `cache.rate_limit_ttl` / `rate_limit_max_requests` | Rate-limit window / max requests per window |
| `auth.yml` | `secret_key` / `algorithm` | JWT signing key and algorithm |
| `auth.yml` | `access_token_expire_minutes` | Token validity (minutes) |

---

## API Reference

The service prefix is `/api`; auth-related endpoints use the `/api/auth` prefix.

### Authentication

| Method | Path | Description | Login required |
| --- | --- | --- | --- |
| POST | `/api/auth/register` | Register a user | No |
| POST | `/api/auth/login` | Log in, returns a JWT token | No |
| GET | `/api/auth/me` | Get current user info | Yes |

### Chat and Sessions

| Method | Path | Description | Login required |
| --- | --- | --- | --- |
| POST | `/api/chat` | Start a conversation (login optional; when logged in, sessions are bound to the user) | Optional |
| GET | `/api/sessions` | List my sessions | Yes |
| GET | `/api/session/{session_id}/messages` | Query session history | Optional (ownership checked) |
| DELETE | `/api/session/{session_id}` | Delete a session | Optional (ownership checked) |

### Others

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/health` | Health check |
| GET | `/` | Service info |

### Request Examples

```bash
# Register
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "123456"}'

# Log in to get a token
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "123456"}'

# Chat with the token
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"query": "Which robot vacuum suits a small apartment?", "session_id": null}'
```

### Unified Response Format

```json
{
  "code": 200,
  "message": "success",
  "data": { "answer": "...", "session_id": "uuid" },
  "request_id": "abc12345",
  "elapsed_ms": 156.78
}
```

---

## Running Tests

```bash
pytest tests/ -v
```

Tests cover JWT encode/decode, password hashing, session data access, and user isolation — i.e. core logic that does not depend on the LLM.

---

## FAQ

**Q: Startup error `password cannot be longer than 72 bytes`?**
passlib 1.7.4 is incompatible with bcrypt 5.x. Make sure `bcrypt==4.0.1` is installed (already pinned in `requirements.txt`).

**Q: Request timeouts or Redis errors?**
When Redis isn't running, the system degrades automatically — chat works normally, only caching and rate limiting are unavailable. If timeouts persist with Redis running, check `host` / `port` / `password` in `config/redis.yml`.

**Q: Foreign-key or field errors after changing ORM models?**
`create_all` does not alter existing table structures. Delete `data/smartsweep_agent.db` and restart the service to rebuild the tables.

**Q: Code changed but endpoint behavior didn't?**
An old uvicorn process may still hold the port. Confirm request logs appear in the terminal, and kill leftover processes before restarting if needed.
On Windows, prefer PowerShell or cmd over running inside PyCharm, which may spawn extra uvicorn processes (orphan processes) or cause reload to not take effect. On macOS, running directly from the command line works fine.

---

## Development Stages

This project evolved from a single-file Streamlit demo into a full backend-engineered application, mainly in these stages:

1. Split out the FastAPI service layer; separate frontend and backend
2. Session management + multi-turn Agent conversation
3. SQLite session persistence
4. RAG retrieval augmentation (vector retrieval + re-ranking)
5. Redis cache / rate limiting + unified response / exception system
6. JWT authentication and user system
7. Security hardening (session authorization protection), docs, and tests

---

## License

Released under the [MIT License](LICENSE).
