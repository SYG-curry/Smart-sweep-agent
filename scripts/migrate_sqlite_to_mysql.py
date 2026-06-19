"""
    若你的SQLite有之前的用户/会话数据
    该脚本用于迁移到MySQL
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from session.models import UserORM, ChatSessionORM, ChatMessageORM

# 旧库
old_engine = create_engine("sqlite:///data/smartsweep_agent.db")
OldSession = sessionmaker(bind=old_engine)

# 新库
new_engine = create_engine("mysq+pymysql://root:password@localhost/smartsweep?charset=utf8mb4")
NewSession = sessionmaker(bind=new_engine)

old_db = OldSession()
new_db = NewSession()

# 迁移用户
for user in old_db.query(UserORM).all():
    new_db.merge(user)      # merge会处理主键冲突

# 迁移会话
for session in old_db.query(ChatSessionORM).all():
    new_db.merge(session)

# 迁移消息
for msg in old_db.query(ChatMessageORM).all():
    new_db.merge(msg)

new_db.commit()
print("迁移完成")










