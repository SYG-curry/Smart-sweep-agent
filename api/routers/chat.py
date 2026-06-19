"""
    接收用户问题
    获取/创建session
    调用Agent
    返回答案
"""
import time, json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from agent.react_agent import ReactAgent
from api.dependencies.rate_limit import rate_limit
from api.context import request_id_var, request_start_time_var
from api.schemas.chat import ChatRequest
from api.schemas.response import ChatApiResponse, ChatData, ApiResponse
from session.session_manager import session_manager
from utils.db import get_db
from utils.logger_handler import logger
from api.dependencies.auth import get_current_user, get_current_user_optional
from api.exceptions.business import SessionNotFoundException, AgentException, ForbiddenException



router = APIRouter()

# 匿名会话没有归属人, 谁持有session_id谁就能访问, 一旦会话绑定用户, 就只有本人能碰, 既保证了匿名聊天的可用性, 又堵死了越权
def _verify_session_access(session, current_user):
    if session.user_id is not None:
        if current_user is None or current_user.id != session.user_id:
            raise ForbiddenException("无权访问该会话")

# SSE格式化函数
def _sse_event(data: dict) -> str:
    """
        SSE 实际传输格式是：
            data: {"type":"thinking","content":"正在检索知识库..."}

            data: {"type":"answer","content":"小户型"}

            data: {"type":"done"}
        每个事件后面要有两个换行。 否则浏览器端的 reader 可能无法正确识别一个事件结束
    """
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

agent = ReactAgent()

@router.post("/chat", response_model=ChatApiResponse)
def chat(
        request: ChatRequest,
        db: Session = Depends(get_db),
        # _ 是一个占位参数，它的目的是把 rate_limiter 作为一个“守卫”依赖挂在这个路由上，请求进来时先执行限流检查，通过了才进入真正的业务逻辑，无需在业务代码里再做判断
        _: None = Depends(rate_limit),
        current_user = Depends(get_current_user_optional),
):
    start_time = request_start_time_var.get()
    request_id = request_id_var.get()

    user_id = current_user.id if current_user else None

    session = session_manager.get_or_create_session(
        db=db,
        session_id=request.session_id,
        user_id=user_id,
    )

    # 获取历史记录, 支持多轮对话, 对应的修改agent.execute_stream方法
    history = session_manager.get_messages(
        db=db,
        session_id=session.id,
    )

    try:
        response_chunks = []
        for chunk in agent.execute_stream(
            query=request.query,
            history=history
        ):
            response_chunks.append(chunk)

        answer = "".join(response_chunks).strip()
    except Exception as e:
        logger.error(f"[chat] Agent执行失败: {e}", exc_info=True)
        raise AgentException(message=f"智能体执行失败: {str(e)}")

    if not answer:
        answer = "抱歉, 我暂时无法回答这个问题"

    session_manager.add_message(
        db=db,
        session_id=session.id,
        role="user",
        content=request.query
    )

    # 写入回答, 维护历史记录
    session_manager.add_message(
        db=db,
        session_id=session.id,
        role="assistant",
        content=answer
    )

    elapsed = (time.time() - start_time) * 1000

    return ChatApiResponse(
        code=200,
        message="success",
        data=ChatData(
            answer=answer,
            session_id=session.id,
        ),
        request_id=request_id,
        elapsed_ms=round(elapsed, 2),
    )

# 流式输出
@router.post("/chat/stream")
def chat_stream(
        request: ChatRequest,
        db: Session = Depends(get_db),
        _: None = Depends(rate_limit),
        current_user = Depends(get_current_user_optional),
):
    request_id = request_id_var.get()
    start_time = request_start_time_var.get()

    user_id = current_user.id if current_user else None

    session = session_manager.get_or_create_session(
        db=db,
        session_id=request.session_id,
        user_id=user_id,
    )

    history = session_manager.get_messages(
        db=db,
        session_id=session.id,
    )

    def event_generator():
        answer_chunks = []

        try:
            # 先把session_id返回给前端
            # 如果这是新对话, 前端需要立即知道新session_id
            yield _sse_event({
                "type": "session",
                "session_id": session.id,
                "request_id": request_id,
            })

            for event in agent.execute_event_stream(
                query=request.query,
                history=history
            ):
                event_type = event.get("type")
                content = event.get("content", "")

                if event_type == "thinking":
                    yield _sse_event({
                        "type": "thinking",
                        "content": content,
                    })
                elif event_type == "answer":
                    answer_chunks.append(content)
                    yield _sse_event({
                        "type": "answer",
                        "content": content,
                    })

            answer = "".join(answer_chunks).strip()

            if not answer:
                answer = "抱歉, 我暂时无法回答这个问题"
                yield _sse_event({
                    "type": "answer",
                    "content": answer,
                })

            # 流式结束后, 再把用户消息和助手消息写入数据库
            # 这里只保存最终答案, 不保存thinking过程
            session_manager.add_message(
                db=db,
                session_id=session.id,
                role="user",
                content=request.query
            )

            session_manager.add_message(
                db=db,
                session_id=session.id,
                role="assistant",
                content=answer
            )

            elapsed = (time.time() - start_time) * 1000

            yield _sse_event({
                "type": "done",
                "request_id": request_id,
                "elapsed_ms": round(elapsed, 2),
            })

        except Exception as e:
            logger.error(f"[chat_stream] Agent执行失败:{e}", exc_info=True)

            yield _sse_event({
                "type": "error",
                "message": f"Agent执行失败: {str(e)}",
            })

    # 普通JSON是: 后端全部生成后 -> 一次性返回
    # StreamingResponse是: 后端生成一点 -> 立刻发给前端 ……
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Request-ID": request_id
        }
    )


# 获取会话历史接口
@router.get("/session/{session_id}/messages")
def get_session_messages(
        session_id: str,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user_optional),
):
    request_id = request_id_var.get()
    start_time = request_start_time_var.get()

    session = session_manager.get_session(db=db, session_id=session_id)
    if not session:
        raise SessionNotFoundException(session_id=session_id)

    _verify_session_access(session, current_user)

    messages = session_manager.get_messages(
        db=db,
        session_id=session_id
    )

    elapsed = (time.time() - start_time) * 1000

    return ApiResponse(
        code=200,
        message="success",
        data={
            "session_id": session_id,
            "messages": [
                {
                    "role": message.role,
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
                }
                for message in messages
            ],
        },
        request_id=request_id,
        elapsed_ms=round(elapsed, 2),
    )

# 获取当前账号下所有会话记录
@router.get("/sessions")
def list_sessions(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user),
):
    request_id = request_id_var.get()
    start_time = request_start_time_var.get()

    sessions = session_manager.list_sessions(db=db, user_id=current_user.id)

    elapsed = (time.time() - start_time) * 1000

    return ApiResponse(
        code=200,
        message="success",
        data={
            "sessions": [
                {
                    "id": session.id,
                    "title": session.title,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                }
                for session in sessions
            ],
        },
        request_id=request_id,
        elapsed_ms=round(elapsed, 2),
    )

@router.delete("/session/{session_id}")
def delete_session(
        session_id: str,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user_optional),
):
    request_id = request_id_var.get()
    start_time = request_start_time_var.get()

    session = session_manager.get_session(db=db, session_id=session_id)
    if not session:
        raise SessionNotFoundException(session_id=session_id)

    _verify_session_access(session, current_user)

    success = session_manager.delete_session(
        db=db,
        session_id=session_id
    )

    elapsed = (time.time() - start_time) * 1000

    return ApiResponse(
        code=200,
        message="success" if success else "删除失败",
        data={
            "session_id": session_id,
            "success": success,
        },
        request_id=request_id,
        elapsed_ms=round(elapsed, 2),
    )


