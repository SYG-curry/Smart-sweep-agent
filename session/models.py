"""
    建立数据库表中的对象关联
"""
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from utils.db import Base


# 一个会话可以有多个消息
class ChatSessionORM(Base):
    __tablename__ = "sessions"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=True, index=True)
    title = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    messages = relationship(
        "ChatMessageORM",       # 关联的模型
        back_populates="session",           # 反向属性名, 类似 外键
        cascade="all, delete-orphan",       # 级联操作, 当你删除一个会话时，它的所有消息也会被自动删除
    )

    user = relationship(
        "UserORM",
        back_populates="sessions",
    )

class ChatMessageORM(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("sessions.id"), index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    metadata_json = Column(Text, nullable=True)

    session = relationship(
        "ChatSessionORM",
        back_populates="messages",
    )

# 一个用户可以有多个对话
class UserORM(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)
    username = Column(String(64), nullable=False, unique=True, index=True)
    password_hash = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)

    sessions = relationship(
        "ChatSessionORM",
        back_populates="user",
        cascade="all, delete-orphan",
    )

# 日志模型
class AppLogORM(Base):
    __tablename__ = "app_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 日志发生时间
    created_at = Column(DateTime, default=datetime.now, index=True)
    # logger名称, 例如 agent, uvicorn, sqlalchemy
    logger_name = Column(String(100), nullable=False, index=True)
    # INFO / WARNING / ERROR / DEBUG
    level = Column(String(20), nullable=False, index=True)
    # logging 内部的 levelno, 例如 INFO=20, ERROR=40
    level_no = Column(Integer, nullable=False)
    # 真正的日志内容
    message = Column(Text, nullable=False)
    # 哪个文件打印出来的内容
    pathname = Column(Text, nullable=True)
    filename = Column(String(255), nullable=True)
    module = Column(String(255), nullable=True)
    # 哪个函数, 哪一行
    func_name = Column(String(255), nullable=True)
    lineno = Column(Integer, nullable=True)
    # 进程和线程信息
    process_id = Column(Integer, nullable=True)
    thread_id = Column(String(64), nullable=True)
    # 请求id, 用于串联一次请求内所有日志
    request_id = Column(String(64), nullable=True, index=True)
    # 异常堆栈, 例如 logger.error(e, exc_info=True)
    exception_text = Column(Text, nullable=True)
    # stack_info=True 时的堆栈信息
    stack_text = Column(Text, nullable=True)
    # runtime 表示运行时产生, file_migration 表示从旧 log 文件迁移
    source = Column(String(30), default="runtime", index=True)
    # 如果是从旧日志迁移来的, 记录原文件和原始行号
    source_log_file = Column(String(500), nullable=True)
    source_log_line = Column(Integer, nullable=True)
    # 扩展字段, 后面可以放 user_id, session_id, 接口路径等
    metadata_json = Column(Text, nullable=True)







