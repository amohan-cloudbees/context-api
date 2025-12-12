"""
Database model for Skills/Agent Profiles
"""
from sqlalchemy import Column, String, TIMESTAMP, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text
from datetime import datetime
from api.models.context import Base


class Skill(Base):
    """Model for storing agent skills/profiles (Context Artifact Type 1)"""
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    skill_id = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)  # Full markdown content
    category = Column(String(100), index=True)  # e.g., 'code-review', 'documentation', 'testing'
    tags = Column(ARRAY(String))  # Searchable tags
    source = Column(String(50), default='anthropic')  # 'anthropic', 'custom', etc.
    source_url = Column(String(500))  # GitHub URL
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "skillId": self.skill_id,
            "title": self.title,
            "description": self.description,
            "content": self.content,
            "category": self.category,
            "tags": self.tags or [],
            "source": self.source,
            "sourceUrl": self.source_url,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }
