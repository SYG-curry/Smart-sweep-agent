import json
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from session.models import ChatSessionORM, ChatMessageORM, UserORM


class SessionRepository:
    def create_session(
            self,
            db: Session,
            user_id: Optional[str] = None,
    ) -> ChatSessionORM:
        session_id = str(uuid.uuid4())

        session = ChatSessionORM(
            id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return session

    def get_session(
            self,
            db: Session,
            session_id: str,
    ) -> Optional[ChatSessionORM]:
        return db.query(ChatSessionORM).filter(
            ChatSessionORM.id == session_id
        ).first()

    def get_or_create_session(
            self,
            db: Session,
            session_id: Optional[str] = None,
            user_id: Optional[str] = None,
    ) -> ChatSessionORM:
        if session_id:
            session = self.get_session(db, session_id)
            if session:
                return session

        return self.create_session(db, user_id=user_id)

    def add_message(
            self,
            db: Session,
            session_id: str,
            role: str,
            content: str,
            metadata: Optional[dict] = None,
    ) -> ChatMessageORM:
        metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else None

        message = ChatMessageORM(
            session_id=session_id,
            role=role,
            content=content,
            metadata_json=metadata_json,
            created_at=datetime.now(),
        )

        db.add(message)

        session = self.get_session(db, session_id)
        if session:
            session.updated_at = datetime.now()
            if not session.title and role == "user":
                session.title = content[:20]

        db.commit()
        db.refresh(message)

        return message

    def get_messages(
            self,
            db: Session,
            session_id: str
    ) -> List[ChatMessageORM]:
        return db.query(ChatMessageORM).filter(
            ChatMessageORM.session_id == session_id
        ).order_by(ChatMessageORM.created_at.asc()).all()

    # 获取会话列表
    def list_sessions(
            self,
            db: Session,
            user_id: Optional[str] = None,
    ) -> List[ChatSessionORM]:
        query = db.query(ChatSessionORM)

        if user_id is not None:
            query = query.filter(ChatSessionORM.user_id == user_id)
        else:
            query = query.filter(ChatSessionORM.user_id.is_(None))

        return query.order_by(ChatSessionORM.updated_at.desc()).all()

    def delete_session(
            self,
            db: Session,
            session_id: str,
    ) -> bool:
        session = self.get_session(db, session_id)

        if not session:
            return False

        db.delete(session)
        db.commit()

        return True

    def get_user(self, db: Session, user_id: str) -> Optional[UserORM]:
        return db.query(UserORM).filter(UserORM.id == user_id).first()

    def get_user_by_username(self, db: Session, username: str) -> Optional[UserORM]:
        return db.query(UserORM).filter(UserORM.username == username).first()

    def create_user(
            self,
            db: Session,
            user_id: str,
            username: str,
            password_hash: str,
    ) -> UserORM:
        user = UserORM(
            id=user_id,
            username=username,
            password_hash=password_hash,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


session_repository = SessionRepository()








