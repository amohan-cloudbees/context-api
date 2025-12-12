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
    conversationHistory: Optional[List[Dict[str, Any]]] = Field(
        default=[],
        description="Dialogue history between user and AI agents"
    )
    status: Optional[Literal["not_started", "in_progress", "blocked", "needs_review", "completed"]] = Field(
        default="in_progress",
        description="Current workflow status"
    )
    blockedBy: Optional[str] = Field(default=None, description="Ticket ID or reason if blocked")
    timestamp: datetime = Field(..., description="Event timestamp")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "Bug Fix in Progress",
                    "summary": "Developer working on authentication bug with AI help",
                    "value": {
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
                        "conversationHistory": [
                            {
                                "role": "user",
                                "aiClient": "Claude",
                                "message": "Can you help me debug the authentication issue?",
                                "timestamp": "2024-12-09T09:55:00Z"
                            },
                            {
                                "role": "assistant",
                                "aiClient": "Claude",
                                "message": "I'll help you investigate the login.py file.",
                                "timestamp": "2024-12-09T09:56:00Z"
                            }
                        ],
                        "status": "in_progress",
                        "blockedBy": None,
                        "timestamp": "2024-12-09T10:00:00Z"
                    }
                },
                {
                    "name": "Blocked Work",
                    "summary": "Work blocked by dependency on another ticket",
                    "value": {
                        "userId": "jane_dev",
                        "sessionId": "session_789",
                        "repoID": "unify_backend",
                        "catalogID": "unify_map",
                        "ticketID": "JIRA-5678",
                        "contextLevel": "ticket",
                        "AI_Client_type": ["AWSQ"],
                        "details": "Cannot implement new API endpoint until database schema is updated",
                        "files": [
                            {
                                "path": "api/routes/users.go",
                                "type": "go",
                                "action": "created"
                            }
                        ],
                        "conversationHistory": [
                            {
                                "role": "user",
                                "aiClient": "AWSQ",
                                "message": "I need to create the /users endpoint but the schema isn't ready",
                                "timestamp": "2024-12-11T14:00:00Z"
                            },
                            {
                                "role": "assistant",
                                "aiClient": "AWSQ",
                                "message": "I see JIRA-4567 handles the schema migration. Let me mark this as blocked.",
                                "timestamp": "2024-12-11T14:01:00Z"
                            }
                        ],
                        "status": "blocked",
                        "blockedBy": "JIRA-4567",
                        "timestamp": "2024-12-11T14:05:00Z"
                    }
                },
                {
                    "name": "New Feature Development",
                    "summary": "Starting fresh feature with multiple files",
                    "value": {
                        "userId": "alice_engineer",
                        "sessionId": "sprint_23_dev",
                        "repoID": "unify_frontend",
                        "catalogID": "unify_map",
                        "ticketID": "JIRA-9999",
                        "contextLevel": "project",
                        "AI_Client_type": ["Claude", "OpenCase"],
                        "details": "Building new dashboard with real-time metrics and data visualization",
                        "files": [
                            {
                                "path": "src/components/Dashboard.tsx",
                                "type": "typescript",
                                "action": "created"
                            },
                            {
                                "path": "src/api/metrics.ts",
                                "type": "typescript",
                                "action": "created"
                            },
                            {
                                "path": "src/styles/dashboard.css",
                                "type": "css",
                                "action": "created"
                            }
                        ],
                        "conversationHistory": [
                            {
                                "role": "user",
                                "aiClient": "Claude",
                                "message": "Help me design a dashboard component that shows real-time system metrics",
                                "timestamp": "2024-12-11T10:00:00Z"
                            },
                            {
                                "role": "assistant",
                                "aiClient": "Claude",
                                "message": "I'll help you create a React dashboard with chart components. Let's start with the structure.",
                                "timestamp": "2024-12-11T10:01:00Z"
                            },
                            {
                                "role": "user",
                                "aiClient": "Claude",
                                "message": "Should I use Chart.js or D3?",
                                "timestamp": "2024-12-11T10:05:00Z"
                            },
                            {
                                "role": "assistant",
                                "aiClient": "Claude",
                                "message": "Chart.js would be simpler for standard metrics. Use D3 only if you need custom visualizations.",
                                "timestamp": "2024-12-11T10:06:00Z"
                            }
                        ],
                        "status": "in_progress",
                        "blockedBy": None,
                        "timestamp": "2024-12-11T10:30:00Z"
                    }
                },
                {
                    "name": "Code Review Context",
                    "summary": "Context for completed work awaiting review",
                    "value": {
                        "userId": "bob_dev",
                        "sessionId": "pr_review_session",
                        "repoID": "unify_services",
                        "catalogID": "unify_map",
                        "ticketID": "JIRA-3456",
                        "contextLevel": "ticket",
                        "AI_Client_type": ["Claude"],
                        "details": "Implemented caching layer for user profile API to reduce database load",
                        "files": [
                            {
                                "path": "services/user_service.py",
                                "type": "python",
                                "action": "modified"
                            },
                            {
                                "path": "cache/redis_client.py",
                                "type": "python",
                                "action": "created"
                            },
                            {
                                "path": "tests/test_user_service.py",
                                "type": "python",
                                "action": "modified"
                            }
                        ],
                        "conversationHistory": [
                            {
                                "role": "user",
                                "aiClient": "Claude",
                                "message": "I've implemented Redis caching. Can you review the code?",
                                "timestamp": "2024-12-11T16:00:00Z"
                            },
                            {
                                "role": "assistant",
                                "aiClient": "Claude",
                                "message": "The implementation looks good. Make sure to add cache invalidation on profile updates.",
                                "timestamp": "2024-12-11T16:05:00Z"
                            }
                        ],
                        "status": "needs_review",
                        "blockedBy": None,
                        "timestamp": "2024-12-11T16:10:00Z"
                    }
                }
            ]
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
