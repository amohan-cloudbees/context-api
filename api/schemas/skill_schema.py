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
    version: str = "1.0.0"
    visibilityScope: str = "organization"
    maintainer: Optional[str] = None
    usageCount: int = 0
    changelogUrl: Optional[str] = None
    installUrl: Optional[str] = None
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
                "version": "1.0.0",
                "visibilityScope": "organization",
                "maintainer": "anthropic",
                "usageCount": 0,
                "changelogUrl": "https://example.com/skills/doc-coauthoring/changelog",
                "installUrl": "https://example.com/skills/doc-coauthoring/install",
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


# Pre-Hook Endpoints Schemas

class SkillUpdateInfo(BaseModel):
    """Information about an available skill update"""
    skillId: str
    name: str
    currentVersion: str
    latestVersion: str
    category: str
    description: str
    changelogUrl: Optional[str] = None
    installUrl: Optional[str] = None
    usageCount: int
    maintainer: str


class SkillUpdatesResponse(BaseModel):
    """Response for GET /api/v1/skills/updates"""
    availableUpdates: List[SkillUpdateInfo] = []
    newSkills: List[SkillUpdateInfo] = []

    class Config:
        json_schema_extra = {
            "example": {
                "availableUpdates": [
                    {
                        "skillId": "security-mcp-threat-model-v1",
                        "name": "Security: Threat Model for MCPs",
                        "currentVersion": "1.1.0",
                        "latestVersion": "1.2.0",
                        "category": "security",
                        "description": "Analyze Model Context Protocol implementations...",
                        "changelogUrl": "https://example.com/skills/threat-model-mcp/changelog",
                        "installUrl": "https://example.com/skills/threat-model-mcp/install",
                        "usageCount": 342,
                        "maintainer": "security-platform-team"
                    }
                ],
                "newSkills": [
                    {
                        "skillId": "jenkins-node22-migration-v1",
                        "name": "CI/CD: Jenkins Pipeline - Node 22 Migration",
                        "currentVersion": "0.0.0",
                        "latestVersion": "1.0.0",
                        "category": "devops",
                        "description": "Migrate Jenkins pipelines to Node.js 22 LTS...",
                        "changelogUrl": None,
                        "installUrl": "https://example.com/skills/jenkins-node22/install",
                        "usageCount": 0,
                        "maintainer": "platform-engineering"
                    }
                ]
            }
        }


class SkillSuggestionRequest(BaseModel):
    """Request for POST /api/v1/skills/suggest"""
    userPrompt: str = Field(..., description="User's task description")
    context: Optional[dict] = Field(default={}, description="Additional context (files, repo, project type)")

    class Config:
        json_schema_extra = {
            "example": {
                "userPrompt": "Review the MCP server security",
                "context": {
                    "filesOpen": ["src/mcp-server.ts", "config/auth.json"],
                    "gitRepo": "github.com/company/mcp-auth-service",
                    "projectType": "typescript"
                }
            }
        }


class SkillSuggestion(BaseModel):
    """A single skill suggestion"""
    skillId: str
    confidence: float
    reasoning: str
    skillMetadata: dict
    installed: bool = Field(default=False, description="Whether the skill is already installed locally")

    class Config:
        json_schema_extra = {
            "example": {
                "skillId": "security-mcp-threat-model-v1",
                "confidence": 0.92,
                "reasoning": "User prompt mentions MCP server security review",
                "skillMetadata": {
                    "name": "Security: Threat Model for MCPs",
                    "description": "Comprehensive security analysis...",
                    "capabilities": ["vulnerability-scanning", "compliance-check"]
                },
                "installed": True
            }
        }


class SkillSuggestionsResponse(BaseModel):
    """Response for POST /api/v1/skills/suggest"""
    suggestions: List[SkillSuggestion] = []

    class Config:
        json_schema_extra = {
            "example": {
                "suggestions": [
                    {
                        "skillId": "security-mcp-threat-model-v1",
                        "confidence": 0.92,
                        "reasoning": "User prompt mentions MCP server security review",
                        "skillMetadata": {
                            "name": "Security: Threat Model for MCPs",
                            "description": "Comprehensive security analysis...",
                            "capabilities": ["vulnerability-scanning", "compliance-check"]
                        }
                    }
                ]
            }
        }


class SkillShareRequest(BaseModel):
    """Request for POST /api/v1/skills/share"""
    skillId: str
    baseVersion: str
    modifiedVersion: str
    changes: dict = Field(..., description="Contains diff, changelog, filesModified")
    shareScope: str = Field(..., description="private, team, organization, global")
    teamId: Optional[str] = None
    notifyUsers: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "skillId": "api-standard-updater-v2",
                "baseVersion": "2.4.0",
                "modifiedVersion": "2.5.0-alpha",
                "changes": {
                    "diff": "...git diff output...",
                    "changelog": "Added GraphQL endpoint validation...",
                    "filesModified": ["validators/graphql.ts", "rules/naming.ts"]
                },
                "shareScope": "team",
                "teamId": "api-platform-team",
                "notifyUsers": True
            }
        }


class SkillShareResponse(BaseModel):
    """Response for POST /api/v1/skills/share"""
    status: str
    message: str
    sharedSkillId: str
    shareUrl: str
    notifiedUsers: int

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Skill modification shared successfully",
                "sharedSkillId": "api-standard-updater-v2.5",
                "shareUrl": "https://example.com/skills/api-standard-updater/v2.5-alpha",
                "notifiedUsers": 12
            }
        }
