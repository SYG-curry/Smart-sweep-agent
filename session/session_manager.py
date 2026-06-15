"""
    创建、读取session
    添加消息
    获取历史消息
"""
from typing import Optional
from sqlalchemy.orm import Session
from session.repository import session_repository


class SessionManager:
    def get_or_create_session(
            self,
            db: Session,
            session_id: Optional[str] = None,
            user_id: Optional[str] = None,
    ):
        return session_repository.get_or_create_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

    def add_message(
            self,
            db: Session,
            session_id: str,
            role: str,
            content: str,
            metadata: Optional[dict] = None,
    ):
        return session_repository.add_message(
            db=db,
            session_id=session_id,
            role=role,
            content=content,
            metadata=metadata,
        )

    def get_session(
            self,
            db: Session,
            session_id: str,
    ):
        return session_repository.get_session(
            db=db,
            session_id=session_id,
        )

    def get_messages(
            self,
            db: Session,
            session_id: str
    ):
        return session_repository.get_messages(
            db=db,
            session_id=session_id,
        )

    def list_sessions(
            self,
            db: Session,
            user_id: Optional[str] = None,
    ):
        return session_repository.list_sessions(
            db=db,
            user_id=user_id,
        )

    def delete_session(
            self,
            db: Session,
            session_id: str,
    ) -> bool:
        return session_repository.delete_session(
            db=db,
            session_id=session_id,
        )

    def get_user(self, db: Session, user_id: str):
        return session_repository.get_user(db=db, user_id=user_id)

    def get_user_by_username(self, db: Session, username: str):
        return session_repository.get_user_by_username(db=db, username=username)

    def create_user(self, db: Session, user_id: str, username: str, password_hash: str):
        return session_repository.create_user(
            db=db,
            user_id=user_id,
            username=username,
            password_hash=password_hash,
        )



session_manager = SessionManager()



