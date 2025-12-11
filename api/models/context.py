"""
Database models for Context API
"""
from sqlalchemy import Column, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class UserContext(Base):
    """Model for storing workflow context data (per ContextPLTC spec)"""
    __tablename__ = "user_contexts"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    context_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)

    # Unify workflow context data (JSONB for flexibility)
    context_data = Column(JSONB, nullable=False)

    timestamp = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "context_id": self.context_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "context_data": self.context_data,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ContextAnalytics(Base):
    """Model for tracking analytics events"""
    __tablename__ = "context_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    context_id = Column(String(255), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    event_data = Column(JSONB, default={})
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "context_id": self.context_id,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
