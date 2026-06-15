import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.db import Base
from session import models  # noqa: F401  确保 ORM 类注册到 Base
from session.repository import session_repository


# 为每个测试提供干净的数据库
@pytest.fixture
def db():
    engine = create_engine(
        # 内存数据库
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    # 根据ORM模型创建所有表
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    try:
        # 把数据库会话传给测试参数
        yield session
    finally:
        session.close()

# 测试用户创建与查询
def test_create_and_get_user(db):
    user = session_repository.create_user(
        db, user_id="u1", username="alice", password_hash="hash",
    )
    assert user.id == "u1"
    fetched = session_repository.get_user_by_username(db, "alice")
    assert fetched is not None
    assert fetched.username == "alice"

# 测试不同用户会话隔离
def test_session_isolation_between_users(db):
    session_repository.create_user(db, user_id="u1", username="alice", password_hash="h")
    session_repository.create_user(db, user_id="u2", username="bob", password_hash="h")
    s1 = session_repository.create_session(db, user_id="u1")
    session_repository.create_session(db, user_id="u2")

    alice_sessions = session_repository.list_sessions(db, user_id="u1")
    assert len(alice_sessions) == 1
    assert alice_sessions[0].id == s1.id

# 测试匿名会话隔离
def test_anonymous_only_sees_anonymous(db):
    session_repository.create_user(db, "u1", "alice", "h")
    session_repository.create_session(db, user_id="u1")
    anon = session_repository.create_session(db, user_id=None)

    result = session_repository.list_sessions(db, user_id=None)
    assert len(result) == 1
    assert result[0].id == anon.id









