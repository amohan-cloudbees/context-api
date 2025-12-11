"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any, Literal
from datetime import datetime


class ContextRequest(BaseModel):
    """Schema for Unify workflow context data (per ContextPLTC spec)"""
    userId: str = Field(..., description="Unique user/developer identifier")
    sessionId: str = Field(..., description="Work session identifier")
    repoID: str = Field(..., description="Repository identifier")
    catalogID: str = Field(..., description="Source catalog (e.g., unify_map)")
    ticketID: str = Field(..., description="Jira or ticket system ID")
    contextLevel: Literal["global", "project", "ticket"] = Field(..., description="Scope of context")
    AI_Client_type: List[str] = Field(..., description="AI tools involved (e.g., Claude, AWSQ, OpenCase)")
    details: str = Field(..., description="Natural language description of user action/goal")
    files: Optional[List[Dict[str, Any]]] = Field(default=[], description="File references")
    timestamp: datetime = Field(..., description="Event timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "userId": "developer123",
                "sessionId": "work_session_456",
                "repoID": "repo_abc123",
                "catalogID": "unify_map",
                "ticketID": "JIRA-1234",
                "contextLevel": "ticket",
                "AI_Client_type": ["Claude", "AWSQ"],
                "details": "I am trying to fix the authentication bug in the login module",
                "files": [
                    {
                        "path": "src/auth/login.py",
                        "type": "python",
                        "action": "modified"
                    }
                ],
                "timestamp": "2024-12-09T10:00:00Z"
            }
        }


class ContextResponse(BaseModel):
    """Schema for API response (per ContextPLTC spec)"""
    status: str = Field(..., description="Response status")
    contextId: str = Field(..., description="Generated context ID")
    details: str = Field(..., description="High-level status information")
    userAlert: Optional[str] = Field(default=None, description="User-facing alert message")
    file: Optional[Dict[str, Any]] = Field(default=None, description="Reference to processed/generated file")
    message: str = Field(..., description="Response message")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "contextId": "ctx_unify_xyz789",
                "details": "Context captured for ticket JIRA-1234 in repo repo_abc123",
                "userAlert": "AI agents are now aware of your JIRA-1234 context",
                "file": {
                    "path": "src/auth/login.py",
                    "status": "tracked"
                },
                "message": "Workflow context successfully stored"
            }
        }


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    status: str = "error"
    error: str
    details: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "error": "ValidationError",
                "details": "repoID is required"
            }
        }
