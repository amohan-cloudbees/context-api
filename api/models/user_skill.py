"""
Database model for User Skills tracking
"""
from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text
from datetime import datetime
from api.models.context import Base


class UserSkill(Base):
    """Model for tracking which skills users have installed"""
    __tablename__ = "user_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id = Column(String(255), nullable=False, index=True)
    skill_id = Column(String(255), nullable=False, index=True)
    installed_version = Column(String(50), nullable=False)
    last_check_timestamp = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "userId": self.user_id,
            "skillId": self.skill_id,
            "installedVersion": self.installed_version,
            "lastCheckTimestamp": self.last_check_timestamp.isoformat() if self.last_check_timestamp else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }
