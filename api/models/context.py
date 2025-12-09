"""
Database models for Context API
"""
from sqlalchemy import Column, String, TIMESTAMP, text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class ContextTypeEnum(str, enum.Enum):
    """Enum for context types"""
    SLACK = "slack"
    UNIFY = "unify"


class UserContext(Base):
    """Model for storing user context data - supports both Slack and Unify contexts"""
    __tablename__ = "user_contexts"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    context_id = Column(String(255), unique=True, nullable=False, index=True)
    context_type = Column(Enum(ContextTypeEnum, values_callable=lambda x: [e.value for e in x]), nullable=False, default=ContextTypeEnum.SLACK, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)

    # Legacy columns (kept for backward compatibility)
    app_context = Column(JSONB, default={})
    conversation_history = Column(JSONB, default=[])
    user_preferences = Column(JSONB, default={})
    device_info = Column(JSONB, default={})
    activity_log = Column(JSONB, default=[])
    location = Column(JSONB, default={})

    # New columns for separated context types
    slack_data = Column(JSONB, default={})
    unify_data = Column(JSONB, default={})

    timestamp = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "context_id": self.context_id,
            "context_type": self.context_type.value if self.context_type else None,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "slack_data": self.slack_data,
            "unify_data": self.unify_data,
            # Legacy fields (for backward compatibility)
            "app_context": self.app_context,
            "conversation_history": self.conversation_history,
            "user_preferences": self.user_preferences,
            "device_info": self.device_info,
            "activity_log": self.activity_log,
            "location": self.location,
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
