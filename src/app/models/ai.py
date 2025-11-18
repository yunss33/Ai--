from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.sqlite import JSON

from app.core.database import Base


class AiConversation(Base):
    __tablename__ = "ai_conversation"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    role_scope = Column(String(20), nullable=False)
    course_id = Column(Integer, ForeignKey("course.id"))
    title = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class AiMessage(Base):
    __tablename__ = "ai_message"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        Integer,
        ForeignKey("ai_conversation.id"),
        nullable=False,
        index=True,
    )
    sender_type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    tool_name = Column(String(100))
    meta = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

