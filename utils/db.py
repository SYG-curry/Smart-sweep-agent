from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from utils.path_tool import get_abs_path


DATABASE_URL = f"sqlite:///{get_abs_path('data/smartsweep_agent.db')}"

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# 会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# 模型基类
Base = declarative_base()

# 依赖注入会话生成器
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



