# SmartSweepAgent · 智扫通机器人智能客服

基于 **LangChain + FastAPI** 构建的扫地机器人领域智能客服 Agent。支持 RAG 知识库问答、多轮对话、用户认证与会话隔离、缓存与限流，是一个具备完整后端工程结构的 AI 应用。

> For English, see [README.en.md](README.en.md)

---

## 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [系统架构](#系统架构)
- [项目结构](#项目结构)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [API 接口](#api-接口)
- [运行测试](#运行测试)
- [常见问题](#常见问题)

---

## 功能特性

| 模块 | 说明 |
| --- | --- |
| **ReAct Agent** | 基于 LangChain，支持工具调用（知识库检索、天气、用户信息、外部数据、报告生成），并通过中间件实现工具监控与动态提示词切换 |
| **RAG 知识库** | Chroma 向量检索 + Reranker 重排，召回 Top-K 候选后精排取 Top-N，提升问答相关性 |
| **多轮对话** | 基于 SQLite 持久化会话，服务重启后历史不丢失 |
| **用户系统** | JWT 认证 + bcrypt 密码哈希，会话按用户隔离，支持匿名访问 |
| **缓存 / 限流** | Redis 缓存 RAG 检索结果、基于 IP+路径的接口限流；Redis 不可用时自动降级，核心功能不受影响 |
| **统一响应** | 所有接口返回 `{code, message, data, request_id, elapsed_ms}` 标准结构，配合全局异常处理与请求追踪 |
| **双入口** | FastAPI 提供标准 REST API；保留 Streamlit 页面用于快速演示 |

---

## 技术栈

- **Web 框架**：FastAPI · Uvicorn · Pydantic
- **LLM / Agent**：LangChain · LangGraph · 通义千问（qwen3-max）
- **RAG**：Chroma · DashScope Embeddings（text-embedding-v4）
- **数据库**：SQLAlchemy + SQLite
- **缓存 / 限流**：Redis
- **认证**：python-jose（JWT）· passlib + bcrypt
- **前端 Demo**：Streamlit

---

## 系统架构

```
                    HTTP 请求
                        │
        ┌───────────────▼────────────────┐
        │  中间件：请求ID / 耗时 / 访问日志   │
        └───────────────┬────────────────┘
                        │
                ┌───────▼────────┐
                │  限流（Redis）   │
                └───────┬────────┘
                        │
              ┌─────────▼──────────┐
              │  API 路由层          │  api/routers
              │  auth / chat / health│
              └─────────┬──────────┘
                        │
         ┌──────────────┼───────────────┐
         │              │               │
  ┌──────▼─────┐ ┌──────▼──────┐ ┌──────▼───────┐
  │ ReactAgent │ │SessionManager│ │  RAG 服务     │
  │ + 工具      │ │ + Repository │ │ 检索+重排+缓存 │
  └──────┬─────┘ └──────┬──────┘ └──────┬───────┘
         │              │               │
   工具/模型调用      SQLite 持久化    Chroma + Redis
```

请求处理链路：中间件注入请求上下文 → 限流校验 → 路由分发 → 业务层（Agent / 会话管理 / RAG）→ 数据层（SQLite / Chroma）→ 统一响应。

---

## 项目结构

```
SmartSweepAgent/
├── api/                   # FastAPI 服务层
│   ├── main.py               # 应用入口：路由注册、中间件、全局异常处理
│   ├── context.py            # 请求级 ContextVar（请求ID、起始时间）
│   ├── routers/              # 路由：auth(认证) / chat(对话) / health(健康检查)
│   ├── schemas/              # Pydantic 请求/响应模型
│   ├── dependencies/         # 依赖注入：auth(JWT校验) / rate_limit(限流)
│   ├── middleware/           # HTTP 中间件：访问日志
│   └── exceptions/           # 业务异常定义
├── agent/                 # 智能体
│   ├── react_agent.py        # ReAct Agent 封装
│   └── tools/                # 工具定义与 Agent 中间件
├── rag/                   # 检索增强
│   ├── vector_store.py       # Chroma 向量库（建库 / 检索）
│   ├── retriever.py          # 混合检索器（检索 + 重排）
│   ├── reranker.py           # 重排序
│   └── rag_service.py        # RAG 主流程（含缓存）
├── session/               # 会话与用户
│   ├── models.py             # SQLAlchemy ORM（users / sessions / messages）
│   ├── repository.py         # 数据库 CRUD
│   └── session_manager.py    # 业务管理层
├── model/
│   └── factory.py            # 模型工厂（Chat / Embedding）
├── utils/                 # 通用工具
│   ├── config_handler.py     # YAML 配置加载
│   ├── db.py                 # 数据库连接与会话
│   ├── redis_client.py       # Redis 连接（含降级）
│   ├── cache.py              # 缓存读写封装
│   ├── jwt_handler.py        # JWT 编解码
│   ├── logger_handler.py     # 日志
│   ├── file_handler.py       # 文件加载与 MD5
│   ├── prompt_loader.py      # 提示词加载
│   └── path_tool.py          # 路径工具
├── config/                # YAML 配置文件
│   ├── agent.yml / chroma.yml / rag.yml / prompts.yml
│   ├── redis.yml / auth.yml
├── prompts/                  # 提示词文本
├── data/                     # 知识库源文件与 SQLite 数据库
├── logs/                     # 运行日志
├── app.py                    # Streamlit Demo 入口
├── requirements.txt
└── README.md
```

---

## 环境要求

- Python 3.10 及以上（开发环境为 3.11）
- Redis（可选，未启动时自动降级，缓存与限流功能不可用但不影响对话）
- 通义千问 / DashScope API Key

---

## 快速开始

### 1. 创建虚拟环境并安装依赖

```bash
conda create -n RAG_Agent python=3.11
conda activate RAG_Agent
pip install -r requirements.txt
```

### 2. 配置 API Key

项目使用通义千问模型，需要设置 DashScope API Key 环境变量：

```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY="你的key"

# Linux / macOS
export DASHSCOPE_API_KEY="你的key"
```

### 3. 检查配置文件

按需修改 `config/` 下的配置（详见[配置说明](#配置说明)）。
**生产环境务必修改 `config/auth.yml` 的 `secret_key`，并妥善保管 `config/redis.yml` 中的密码。**

### 4. 构建知识库（首次运行）

将知识文档放入 `data/` 目录（支持 `.txt` / `.pdf`），然后构建向量库：

```bash
python -m rag.vector_store
```

> 通过文件 MD5 去重，重复运行不会重复入库。

### 5. 启动 API 服务

```bash
python -m uvicorn api.main:app --port 8000
```

启动后访问交互式文档：`http://127.0.0.1:8000/docs`

### 6.（可选）启动 Streamlit Demo

```bash
streamlit run app.py
```

---

## 配置说明

所有配置位于 `config/` 目录，均为 YAML 格式。

| 文件 | 关键项 | 说明 |
| --- | --- | --- |
| `rag.yml` | `chat_model_name` / `embedding_model_name` | 对话模型与向量模型名称 |
| `chroma.yml` | `retriever_k` / `rerank_top_k` | 向量检索召回数量 / 重排后保留数量 |
| `chroma.yml` | `chunk_size` / `chunk_overlap` | 文档切分大小与重叠 |
| `chroma.yml` | `data_path` / `persist_directory` | 知识库源目录 / 向量库持久化目录 |
| `agent.yml` | `external_data_path` | 外部用户数据文件路径 |
| `prompts.yml` | `*_prompt_path` | 各场景提示词文件路径 |
| `redis.yml` | `host` / `port` / `password` | Redis 连接信息 |
| `redis.yml` | `cache.rag_ttl` | RAG 缓存过期时间（秒） |
| `redis.yml` | `cache.rate_limit_ttl` / `rate_limit_max_requests` | 限流窗口时长 / 窗口内最大请求数 |
| `auth.yml` | `secret_key` / `algorithm` | JWT 签名密钥与算法 |
| `auth.yml` | `access_token_expire_minutes` | Token 有效期（分钟） |

---

## API 接口

服务前缀为 `/api`，认证相关接口前缀为 `/api/auth`。

### 认证

| 方法 | 路径 | 说明 | 是否需登录 |
| --- | --- | --- | --- |
| POST | `/api/auth/register` | 用户注册 | 否 |
| POST | `/api/auth/login` | 登录，返回 JWT Token | 否 |
| GET | `/api/auth/me` | 获取当前用户信息 | 是 |

### 对话与会话

| 方法 | 路径 | 说明 | 是否需登录 |
| --- | --- | --- | --- |
| POST | `/api/chat` | 发起对话（支持可选登录，登录后会话绑定用户） | 可选 |
| GET | `/api/sessions` | 获取我的会话列表 | 是 |
| GET | `/api/session/{session_id}/messages` | 查询会话历史消息 | 可选（校验归属） |
| DELETE | `/api/session/{session_id}` | 删除会话 | 可选（校验归属） |

### 其它

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/health` | 健康检查 |
| GET | `/` | 服务信息 |

### 请求示例

```bash
# 注册
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "123456"}'

# 登录获取 token
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "123456"}'

# 携带 token 对话
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <你的token>" \
  -d '{"query": "小户型适合什么扫地机器人？", "session_id": null}'
```

### 统一响应格式

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

## 运行测试

```bash
pytest tests/ -v
```

测试覆盖 JWT 编解码、密码哈希、会话数据访问与用户隔离等不依赖 LLM 的核心逻辑。

---

## 常见问题(亲测)

**Q: 启动报错 `password cannot be longer than 72 bytes`？**
passlib 1.7.4 与 bcrypt 5.x 不兼容。请确保安装 `bcrypt==4.0.1`（已在 `requirements.txt` 锁定）。

**Q: 请求超时或 Redis 报错？**
未启动 Redis 时系统会自动降级，对话功能正常，仅缓存与限流不可用。若已启动 Redis 仍超时，检查 `config/redis.yml` 的 host / port / password。

**Q: 修改了 ORM 模型后报外键或字段错误？**
`create_all` 不会修改已存在的表结构。删除 `data/smartsweep_agent.db` 后重启服务以重建表。

**Q: 改了代码但接口行为没变化？**
可能是旧的 uvicorn 进程仍占用端口。先确认终端有请求日志，必要时查杀残留进程后重启。
注意别在pycharm中运行，pycharm会自动启动uvicorn进程，会导致端口被占用，无法退出程序的情况(孤儿进程)，也会存在reload不生效情况。
Mac可以直接在命令行中运行不会出现问题，Win系统建议在powershell或者cmd中运行，基本不会出现问题

---

## 开发阶段说明

本项目从 Streamlit 单文件 Demo 逐步演进为完整后端工程，主要阶段：

1. 拆分 FastAPI 服务层，前后端分离
2. 会话管理 + Agent 多轮对话
3. SQLite 会话持久化
4. RAG 检索增强（向量检索 + 重排）
5. Redis 缓存 / 限流 + 统一响应 / 异常体系
6. JWT 认证与用户系统
7. 安全加固（会话越权防护）、文档与测试完善
"# Smart-sweep-agent" 
