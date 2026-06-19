# SmartSweepAgent · 智扫通机器人智能客服

基于 **LangChain + FastAPI + Vue 3** 构建的扫地机器人领域智能客服 Agent。支持 RAG 知识库问答、多轮对话、用户认证与会话隔离、SSE 流式输出、Redis 缓存/限流以及 MySQL 日志持久化，是一个从 Agent Demo 演进而来的前后端分离 AI 应用。

> For English, see [README.en.md](README.en.md)

---

## 版本说明

| 版本 | 说明 |
| --- | --- |
| `v0.1.0` | 初始版本：基础 RAG Agent、FastAPI 后端和初始聊天能力 |
| `v0.2.0` | 当前版本：多用户认证、会话隔离、Vue 聊天界面、SSE 流式输出、MySQL 日志持久化 |

> 旧版本可在 GitHub 的 **Tags / Releases** 中选择 `v0.1.0` 查看。

---

## 功能特性

| 模块 | 说明 |
| --- | --- |
| **ReAct Agent** | 基于 LangChain，支持知识库检索、天气、用户信息、外部数据、报告生成等工具调用 |
| **RAG 知识库** | Chroma 向量检索 + Reranker 重排，召回 Top-K 后精排 Top-N |
| **多轮对话** | 会话与消息持久化到数据库，支持历史消息、会话列表和删除会话 |
| **用户系统** | JWT 认证 + bcrypt 密码哈希，会话按用户隔离 |
| **SSE 流式聊天** | `/api/chat/stream` 输出 `session` / `thinking` / `answer` / `done` / `error` 事件 |
| **前端界面** | Vue 3 + Pinia + Vue Router，支持登录注册、会话列表、Markdown 渲染和思考过程展示 |
| **缓存 / 限流** | Redis 缓存 RAG 检索结果，并基于 IP+路径限流；Redis 不可用时自动降级 |
| **统一响应** | REST API 返回 `{code, message, data, request_id, elapsed_ms}` 标准结构 |
| **日志入库** | 运行日志通过异步队列写入 MySQL `app_logs` 表，支持旧日志迁移 |

---

## v0.2.0 主要更新

相比 `v0.1.0`，当前版本主要优化：

- 新增 Vue 3 前端工程，完成登录、注册、聊天主页面和会话列表。
- 新增 JWT 用户认证和 `/api/auth/me` 当前用户校验。
- 新增多用户会话隔离，登录用户只能访问自己的会话。
- 新增前端 `authStore` / `chatStore` 状态管理，修复切换用户时旧聊天内容残留的问题。
- 新增 `/api/chat/stream` SSE 流式聊天接口，前端按事件类型渲染思考过程和最终答案。
- 优化 Agent 流式输出事件，将最终答案统一输出为 `answer` 类型。
- 新增 MySQL 支持，数据库连接通过 `DATABASE_URL` 配置。
- 新增 `app_logs` 日志表和 `DatabaseLogHandler`，运行日志可写入 MySQL。
- 新增 `scripts/migrate_logs_to_mysql.py` 和 `scripts/migrate_sqlite_to_mysql.py`。
- 优化 `.gitignore`，避免提交环境变量、运行日志、数据库文件和构建产物。

---

## 技术栈

- **后端框架**：FastAPI · Uvicorn · Pydantic
- **LLM / Agent**：LangChain · LangGraph · 通义千问（qwen3-max）
- **RAG**：Chroma · DashScope Embeddings（text-embedding-v4）
- **数据库**：SQLAlchemy · MySQL（推荐）· SQLite fallback
- **缓存 / 限流**：Redis
- **认证**：python-jose（JWT）· passlib + bcrypt
- **前端**：Vue 3 · Vite · Pinia · Vue Router · Axios · markdown-it
- **日志**：Python logging · QueueHandler / QueueListener · MySQL `app_logs`
- **演示入口**：Streamlit

---

## 系统架构

```text
HTTP / SSE 请求
   │
   ▼
FastAPI Middleware（request_id / 耗时 / 访问日志）
   │
   ▼
Rate Limit（Redis，可降级）
   │
   ▼
API Routers（auth / chat / health）
   │
   ├── ReactAgent + Tools → LLM / 工具调用
   ├── SessionManager → MySQL / SQLite
   ├── RAG Service → Chroma + Redis
   └── Logger → QueueHandler → DatabaseLogHandler → app_logs
```

---

## 项目结构

```text
SmartSweepAgent/
├── api/                         # FastAPI 服务层
├── agent/                       # ReAct Agent 与工具
├── rag/                         # 向量检索、重排、RAG 服务
├── session/                     # 用户、会话、消息、日志 ORM
├── model/                       # 模型工厂
├── utils/                       # 配置、数据库、Redis、JWT、日志等工具
├── frontend/smartsweep-fronted/ # Vue 3 前端
├── scripts/                     # 日志迁移、SQLite 到 MySQL 迁移脚本
├── config/                      # YAML 配置文件
├── prompts/                     # 提示词文本
├── data/                        # 知识库源文件，本地数据库不提交
├── tests/                       # 单元测试
├── app.py                       # Streamlit Demo
├── requirements.txt             # 后端依赖
├── README.md
└── README.en.md
```

---

## 环境要求

- Python 3.10+（开发环境为 3.11）
- Node.js `^20.19.0 || >=22.12.0`
- MySQL 8.x（推荐；也可使用 SQLite fallback）
- Redis（可选，未启动时自动降级）
- 通义千问 / DashScope API Key

---

## 快速开始

### 1. 安装后端依赖

```bash
conda create -n RAG_Agent python=3.11
conda activate RAG_Agent
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，并按本机环境修改：

```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/smartsweep?charset=utf8mb4
DASHSCOPE_API_KEY=your_dashscope_api_key
```

如果使用 SQLite fallback：

```env
DATABASE_URL=sqlite:///data/smartsweep_agent.db
```

### 3. 检查 MySQL

```bash
python test_mysql_connection.py
```

该脚本会检查 MySQL 连接，并在数据库不存在时创建数据库。表结构会在 FastAPI 启动时自动创建。

> 当前仍为开发阶段，暂未引入 Alembic。生产项目建议使用 Alembic 管理数据库迁移。

### 4. 构建知识库

将知识文档放入 `data/` 目录（支持 `.txt` / `.pdf`），然后构建向量库：

```bash
python -m rag.vector_store
```

### 5. 启动后端

```bash
python -m uvicorn api.main:app --port 8000
```

接口文档：`http://127.0.0.1:8000/docs`

### 6. 启动前端

```bash
cd frontend/smartsweep-fronted
npm install
npm run dev
```

默认前端地址：`http://localhost:5173`

---

## API 接口

### 认证

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 登录并返回 JWT Token |
| GET | `/api/auth/me` | 获取当前用户信息 |

### 对话与会话

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/chat` | 普通对话，返回完整 JSON |
| POST | `/api/chat/stream` | SSE 流式对话 |
| GET | `/api/sessions` | 获取当前用户会话列表 |
| GET | `/api/session/{session_id}/messages` | 查询会话历史消息 |
| DELETE | `/api/session/{session_id}` | 删除会话 |

### SSE 事件

| 类型 | 说明 |
| --- | --- |
| `session` | 返回当前会话 ID |
| `thinking` | 展示 Agent 执行过程 |
| `answer` | 最终答案片段 |
| `done` | 响应结束 |
| `error` | 响应失败 |

---

## 日志与迁移

当前版本支持将运行日志写入 MySQL `app_logs` 表：

```text
logger → QueueHandler → QueueListener → DatabaseLogHandler → app_logs
```

迁移旧日志：

```bash
python scripts/migrate_logs_to_mysql.py
```

迁移 SQLite 数据到 MySQL：

```bash
python scripts/migrate_sqlite_to_mysql.py
```

---

## 运行测试

```bash
pytest tests/ -v
```

前端构建验证：

```bash
cd frontend/smartsweep-fronted
npm run build
```

---

## 常见问题（亲测）

**Q: 启动报错 `password cannot be longer than 72 bytes`？**  
passlib 1.7.4 与 bcrypt 5.x 不兼容。请确保安装 `bcrypt==4.0.1`。

**Q: 请求超时或 Redis 报错？**  
未启动 Redis 时系统会自动降级，对话功能正常，仅缓存与限流不可用。若 Redis 已启动仍超时，请检查 `config/redis.yml`。

**Q: 修改 ORM 模型后字段没有生效？**  
`Base.metadata.create_all()` 只会创建不存在的表，不会修改已存在表结构。开发期可以删除本地测试数据库后重启服务；MySQL 环境建议手动调整表结构，后续应引入 Alembic。

**Q: 改了代码但接口行为没变化？**  
可能是旧 uvicorn 进程仍占用端口。Windows 建议使用 PowerShell 或 cmd 启动，不建议长期依赖 PyCharm 自动运行，避免残留孤儿进程导致端口占用或 reload 不生效。

**Q: 切换 user1 / user2 后，主聊天区显示了上一个用户的对话？**  
这是前端单页应用状态生命周期问题。`chatStore` 是全局状态，如果登出或重新登录时不清空 `messages`、`currentSessionId`、`sessions`，主聊天区会残留上一个用户的消息。当前版本通过 `chatStore.reset()`，并在 login / logout / ChatView mounted / 路由校验中重新同步用户状态解决。

**Q: token 隔天看起来仍然有效，左下角却没有用户名？**  
原问题是前端只根据 localStorage 中是否存在 token 判断登录态，没有进入页面前调用 `/api/auth/me` 校验 token 是否真实有效，也没有保证 `userInfo` 已加载。当前版本增加了 token 过期时间记录和 `ensureUserInfo()`。
---

## 开发阶段说明

本项目从 Streamlit 单文件 Demo 逐步演进为完整前后端分离应用：

1. FastAPI 服务层拆分和前后端分离。
2. 会话管理 + Agent 多轮对话。
3. SQLite 会话持久化。
4. RAG 检索增强（向量检索 + 重排）。
5. Redis 缓存 / 限流 + 统一响应 / 异常体系。
6. JWT 认证与用户系统。
7. Vue 3 前端界面、会话列表、Markdown 消息渲染。
8. SSE 流式聊天与 thinking / answer 分区展示。
9. MySQL 持久化、日志入库与历史日志迁移。
10. 多用户切换、token 校验、认证状态一致性修复。

---

## 后续计划

- 引入 Alembic 管理数据库迁移。
- 增加 Docker Compose，一键启动 MySQL / Redis / Backend / Frontend。
- 增加日志查询后台和错误统计页面。
- 增强 RAG 引用来源展示和知识库管理能力。
- 增加更完整的后端 API 测试和前端状态测试。

---

## License

Released under the [MIT License](LICENSE).
