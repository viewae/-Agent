from __future__ import annotations

import json
import uuid

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.conversation import Conversation, MessageRole


class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    def create_or_get_session(self, session_id: str | None) -> str:
        return session_id or uuid.uuid4().hex[:16]

    def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: dict | None = None,
    ) -> Conversation:
        msg = Conversation(
            session_id=session_id,
            role=role,
            content=content,
            metadata_json=json.dumps(metadata, ensure_ascii=False) if metadata else None,
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_session_history(self, session_id: str) -> list[dict]:
        msgs = (
            self.db.query(Conversation)
            .filter(Conversation.session_id == session_id)
            .order_by(Conversation.created_at.asc())
            .all()
        )
        return [{"role": m.role, "content": m.content} for m in msgs]

    def get_user_sessions(self) -> list[dict]:
        # Single query with aggregated count — avoids N+1
        rows = (
            self.db.query(
                Conversation.session_id,
                Conversation.content,
                Conversation.created_at,
                func.count(Conversation.id).label("msg_count"),
            )
            .filter(Conversation.role == MessageRole.USER.value)
            .group_by(Conversation.session_id)
            .order_by(Conversation.created_at.desc())
            .all()
        )
        result = []
        seen = set()
        for sid, query, ts, count in rows:
            if sid in seen:
                continue
            seen.add(sid)
            result.append({
                "session_id": sid,
                "first_query": query[:100] if query else "",
                "message_count": count,
                "created_at": ts.isoformat() if ts else "",
            })
        return result

    def delete_session(self, session_id: str) -> None:
        self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).delete()
        self.db.commit()
