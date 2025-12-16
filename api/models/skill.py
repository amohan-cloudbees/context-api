"""
Database model for Skills/Agent Profiles
"""
from sqlalchemy import Column, String, TIMESTAMP, Text, ARRAY, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
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
    version = Column(String(50), default='1.0.0', index=True)  # Semantic version
    visibility_scope = Column(String(20), default='organization', index=True)  # private, team, organization, global
    maintainer = Column(String(255), index=True)  # Team or individual maintaining the skill
    usage_count = Column(Integer, default=0)  # Number of times skill has been activated
    changelog_url = Column(String(500))  # URL to changelog documentation
    install_url = Column(String(500))  # URL for installing/viewing the skill
    embedding = Column(JSONB)  # Vector embedding for semantic search (1024-dim array)
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
            "version": self.version,
            "visibilityScope": self.visibility_scope,
            "maintainer": self.maintainer,
            "usageCount": self.usage_count,
            "changelogUrl": self.changelog_url,
            "installUrl": self.install_url,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }
