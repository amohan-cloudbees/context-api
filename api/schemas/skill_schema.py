"""
Pydantic schemas for Skills API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SkillResponse(BaseModel):
    """Schema for skill response"""
    skillId: str
    title: str
    description: Optional[str] = None
    content: str
    category: Optional[str] = None
    tags: List[str] = []
    source: str = "anthropic"
    sourceUrl: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "skillId": "doc-coauthoring",
                "title": "Document Co-Authoring Workflow",
                "description": "Guide users through structured workflow for co-authoring documentation",
                "content": "# Doc Co-Authoring Workflow\n\nThis skill provides...",
                "category": "documentation",
                "tags": ["documentation", "writing", "collaboration"],
                "source": "anthropic",
                "sourceUrl": "https://github.com/anthropics/skills/tree/main/skills/doc-coauthoring",
                "createdAt": "2024-12-11T20:00:00",
                "updatedAt": "2024-12-11T20:00:00"
            }
        }


class SkillSearchResponse(BaseModel):
    """Schema for skill search results"""
    status: str
    count: int
    filters: dict
    data: List[SkillResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "count": 2,
                "filters": {
                    "category": "documentation",
                    "query": "writing"
                },
                "data": [
                    {
                        "skillId": "doc-coauthoring",
                        "title": "Document Co-Authoring Workflow",
                        "description": "Guide users through structured workflow...",
                        "category": "documentation",
                        "tags": ["documentation", "writing"]
                    }
                ]
            }
        }


class SkillIngestionRequest(BaseModel):
    """Schema for manual skill upload (for custom skills later)"""
    skillId: str = Field(..., description="Unique skill identifier")
    title: str = Field(..., description="Skill title")
    description: Optional[str] = Field(None, description="Brief description")
    content: str = Field(..., description="Full skill content (markdown)")
    category: Optional[str] = Field(None, description="Skill category")
    tags: Optional[List[str]] = Field(default=[], description="Tags for searchability")
    source: str = Field(default="custom", description="Source system")
    sourceUrl: Optional[str] = Field(None, description="Reference URL")


class IngestionResponse(BaseModel):
    """Schema for ingestion operation response"""
    status: str
    message: str
    skillsIngested: int
    skillsSkipped: int
    details: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Successfully ingested skills from Anthropic repository",
                "skillsIngested": 11,
                "skillsSkipped": 5,
                "details": [
                    "Ingested: doc-coauthoring",
                    "Ingested: webapp-testing",
                    "Skipped: algorithmic-art (not engineering-related)",
                    "Skipped: slack-gif-creator (not engineering-related)"
                ]
            }
        }
