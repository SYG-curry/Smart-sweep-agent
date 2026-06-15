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



