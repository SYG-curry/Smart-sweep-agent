# SmartSweepAgent · Robot Vacuum AI Customer-Service Agent

SmartSweepAgent is a robot-vacuum-domain AI customer-service Agent built with **LangChain + FastAPI + Vue 3**. It supports RAG knowledge-base Q&A, multi-turn conversations, user authentication with session isolation, SSE streaming responses, Redis-based caching/rate limiting, and MySQL-backed log persistence.

> 中文文档见 [README.md](README.md)

---

## Version Notes

| Version | Description |
| --- | --- |
| `v0.1.0` | Initial version: basic RAG Agent, FastAPI backend, and initial chat capability |
| `v0.2.0` | Current version: user authentication, session isolation, Vue chat UI, SSE streaming, and MySQL log persistence |

> Older versions can be viewed from GitHub **Tags / Releases**, for example `v0.1.0`.

---

## Features

| Module | Description |
| --- | --- |
| **ReAct Agent** | Built on LangChain, with tool calling for knowledge retrieval, weather, user info, external data, and report generation |
| **RAG Knowledge Base** | Chroma vector retrieval + Reranker re-ranking: recall Top-K candidates and keep the most relevant Top-N |
| **Multi-turn Chat** | Sessions and messages are persisted in the database, with history loading, session list, and session deletion |
| **User System** | JWT authentication + bcrypt password hashing, with per-user session isolation |
| **SSE Streaming Chat** | `/api/chat/stream` emits `session` / `thinking` / `answer` / `done` / `error` events |
| **Frontend UI** | Vue 3 + Pinia + Vue Router, with login/register, session list, Markdown rendering, and thinking-process display |
| **Cache / Rate Limit** | Redis caches RAG retrieval results and rate-limits by IP+path; gracefully degrades when Redis is unavailable |
| **Unified Response** | REST APIs return `{code, message, data, request_id, elapsed_ms}` consistently |
| **Database Logging** | Runtime logs are written asynchronously to the MySQL `app_logs` table, with migration support for old log files |

---

## v0.2.0 Highlights

Compared with `v0.1.0`, the current version adds and improves:

- Vue 3 frontend project with login, registration, chat page, and session list.
- JWT authentication and `/api/auth/me` current-user validation.
- Per-user session isolation so users only access their own conversations.
- Pinia `authStore` / `chatStore` state management, including fixes for stale chat content after switching users.
- `/api/chat/stream` SSE endpoint with event-based rendering for thinking and final answer output.
- Improved Agent streaming events, with final responses normalized as `answer` events.
- MySQL support through the `DATABASE_URL` environment variable.
- `app_logs` table and `DatabaseLogHandler` for database-backed runtime logs.
- `scripts/migrate_logs_to_mysql.py` and `scripts/migrate_sqlite_to_mysql.py` migration scripts.
- Improved `.gitignore` to avoid committing environment files, runtime logs, local databases, and build artifacts.

---

## Tech Stack

- **Backend Framework**: FastAPI · Uvicorn · Pydantic
- **LLM / Agent**: LangChain · LangGraph · Tongyi Qianwen (qwen3-max)
- **RAG**: Chroma · DashScope Embeddings (text-embedding-v4)
- **Database**: SQLAlchemy · MySQL (recommended) · SQLite fallback
- **Cache / Rate Limit**: Redis
- **Auth**: python-jose (JWT) · passlib + bcrypt
- **Frontend**: Vue 3 · Vite · Pinia · Vue Router · Axios · markdown-it
- **Logging**: Python logging · QueueHandler / QueueListener · MySQL `app_logs`
- **Demo Entry**: Streamlit

---

## Architecture

```text
HTTP / SSE Request
   │
   ▼
FastAPI Middleware (request_id / timing / access log)
   │
   ▼
Rate Limit (Redis, graceful fallback)
   │
   ▼
API Routers (auth / chat / health)
   │
   ├── ReactAgent + Tools → LLM / tool calls
   ├── SessionManager → MySQL / SQLite
   ├── RAG Service → Chroma + Redis
   └── Logger → QueueHandler → DatabaseLogHandler → app_logs
```

---

## Project Structure

```text
SmartSweepAgent/
├── api/                         # FastAPI service layer
├── agent/                       # ReAct Agent and tools
├── rag/                         # Vector retrieval, re-ranking, RAG service
├── session/                     # User, session, message, and log ORM models
├── model/                       # Model factory
├── utils/                       # Config, database, Redis, JWT, logging utilities
├── frontend/smartsweep-fronted/ # Vue 3 frontend
├── scripts/                     # Log migration and SQLite-to-MySQL migration scripts
├── config/                      # YAML config files
├── prompts/                     # Prompt templates
├── data/                        # Knowledge-base source files; local DB files are ignored
├── tests/                       # Unit tests
├── app.py                       # Streamlit demo
├── requirements.txt             # Backend dependencies
├── README.md
└── README.en.md
```

---

## Requirements

- Python 3.10+ (developed on 3.11)
- Node.js `^20.19.0 || >=22.12.0`
- MySQL 8.x (recommended; SQLite fallback is also supported)
- Redis (optional; disabled gracefully when unavailable)
- Tongyi Qianwen / DashScope API Key

---

## Quick Start

### 1. Install backend dependencies

```bash
conda create -n RAG_Agent python=3.11
conda activate RAG_Agent
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and update it for your local machine:

```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/smartsweep?charset=utf8mb4
DASHSCOPE_API_KEY=your_dashscope_api_key
```

For SQLite fallback:

```env
DATABASE_URL=sqlite:///data/smartsweep_agent.db
```

### 3. Check MySQL

```bash
python test_mysql_connection.py
```

This script checks the MySQL connection and creates the database if it does not exist. Tables are created automatically when the FastAPI app starts.

> This project is still in the development stage and does not use Alembic yet. Production projects should use Alembic for database migrations.

### 4. Build the knowledge base

Put knowledge documents into the `data/` directory (`.txt` / `.pdf` supported), then build the vector store:

```bash
python -m rag.vector_store
```

### 5. Start the backend

```bash
python -m uvicorn api.main:app --port 8000
```

API docs: `http://127.0.0.1:8000/docs`

### 6. Start the frontend

```bash
cd frontend/smartsweep-fronted
npm install
npm run dev
```

Default frontend URL: `http://localhost:5173`

---

## API Reference

### Authentication

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/auth/register` | Register a user |
| POST | `/api/auth/login` | Log in and return a JWT token |
| GET | `/api/auth/me` | Get current user info |

### Chat and Sessions

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/chat` | Normal chat endpoint returning full JSON |
| POST | `/api/chat/stream` | SSE streaming chat endpoint |
| GET | `/api/sessions` | List current user's sessions |
| GET | `/api/session/{session_id}/messages` | Query session history |
| DELETE | `/api/session/{session_id}` | Delete a session |

### SSE Events

| Type | Description |
| --- | --- |
| `session` | Returns the current session ID |
| `thinking` | Shows the Agent execution process |
| `answer` | Final answer chunk |
| `done` | Stream completed |
| `error` | Stream failed |

---

## Logging and Migration

Runtime logs can be written to the MySQL `app_logs` table:

```text
logger → QueueHandler → QueueListener → DatabaseLogHandler → app_logs
```

Migrate old log files:

```bash
python scripts/migrate_logs_to_mysql.py
```

Migrate SQLite data to MySQL:

```bash
python scripts/migrate_sqlite_to_mysql.py
```

---

## Running Tests

```bash
pytest tests/ -v
```

Frontend build check:

```bash
cd frontend/smartsweep-fronted
npm run build
```

---

## FAQ (Tested During Development)

**Q: Startup error `password cannot be longer than 72 bytes`?**  
passlib 1.7.4 is incompatible with bcrypt 5.x. Make sure `bcrypt==4.0.1` is installed.

**Q: Request timeout or Redis errors?**  
When Redis is not running, the system degrades automatically. Chat still works; only caching and rate limiting are unavailable. If Redis is running but errors persist, check `config/redis.yml`.

**Q: ORM model changes do not appear in the database?**  
`Base.metadata.create_all()` only creates missing tables; it does not alter existing table structures. During development, you can recreate the local test database. For MySQL, update the schema manually or introduce Alembic later.

**Q: Code changed but API behavior did not?**  
An old uvicorn process may still be holding the port. On Windows, PowerShell or cmd is preferred over long-running PyCharm auto-run sessions, which may leave orphan processes or make reload ineffective.

**Q: After switching from user1 to user2, the main chat area still shows user1's messages?**  
This is a frontend SPA state-lifecycle issue. `chatStore` is global state; if `messages`, `currentSessionId`, and `sessions` are not reset during logout/login, stale messages remain visible. The current version fixes this with `chatStore.reset()` and user-state synchronization during login, logout, ChatView mounting, and route checks.

**Q: A token appears valid the next day, but the username is missing in the lower-left corner?**  
The original issue was that the frontend only checked whether a token existed in localStorage. It did not call `/api/auth/me` before entering protected pages, and `userInfo` was not guaranteed to be loaded. The current version adds token-expiration tracking and `ensureUserInfo()`.
---

## Development Stages

This project evolved from a single-file Streamlit demo into a frontend/backend separated application:

1. FastAPI service layer and frontend/backend separation.
2. Session management and multi-turn Agent conversation.
3. SQLite session persistence.
4. RAG retrieval augmentation with vector retrieval and re-ranking.
5. Redis caching/rate limiting, unified response, and exception system.
6. JWT authentication and user system.
7. Vue 3 frontend UI, session list, and Markdown message rendering.
8. SSE streaming chat with thinking/answer display.
9. MySQL persistence, database-backed logging, and historical log migration.
10. User-switching, token validation, and authentication-state consistency fixes.

---

## Roadmap

- Introduce Alembic for database migrations.
- Add Docker Compose for MySQL / Redis / Backend / Frontend.
- Add log-query dashboard and error statistics.
- Improve RAG source citation and knowledge-base management.
- Add more complete backend API tests and frontend state tests.

---

## License

Released under the [MIT License](LICENSE).
