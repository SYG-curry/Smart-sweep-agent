import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from utils.path_tool import get_abs_path

# 读取env
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{get_abs_path('data/smartsweep_agent.db')}"
)

# 如果是SQLite, 则设置check_same_thread为False(特有参数)
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_size=10,           # 连接池大小(SQLite无效, MySQL有效)
    max_overflow=20,        # 允许临时超出的连接数
    pool_pre_ping=True,     # 每次连接前先ping, 防止连接断开
    pool_recycle=3600,      # 1h回收连接, 防止MySQL超时
)

# 会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()






