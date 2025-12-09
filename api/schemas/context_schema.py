"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any, Literal
from datetime import datetime


# ============ SLACK CONTEXT SCHEMAS ============

class SlackContextRequest(BaseModel):
    """Schema for Slack conversational context data"""
    userId: str = Field(..., description="Unique user identifier")
    sessionId: str = Field(..., description="Session identifier")
    appContext: Optional[Dict[str, Any]] = Field(default={}, description="Application-specific context")
    conversationHistory: Optional[List[Dict[str, Any]]] = Field(default=[], description="Conversation messages")
    userPreferences: Optional[Dict[str, Any]] = Field(default={}, description="User preferences")
    deviceInfo: Optional[Dict[str, Any]] = Field(default={}, description="Device information")
    activityLog: Optional[List[Dict[str, Any]]] = Field(default=[], description="User activity log")
    location: Optional[Dict[str, str]] = Field(default={}, description="Location data")
    timestamp: datetime = Field(..., description="Event timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "userId": "user123",
                "sessionId": "session456",
                "appContext": {
                    "appName": "SlackBot",
                    "channel": "general",
                    "threadTs": "1234567890.123456"
                },
                "conversationHistory": [
                    {
                        "role": "user",
                        "message": "What are your business hours?",
                        "timestamp": "2024-12-09T10:00:00Z"
                    }
                ],
                "userPreferences": {
                    "theme": "dark",
                    "language": "en",
                    "notifications": True
                },
                "deviceInfo": {
                    "platform": "slack",
                    "client": "web"
                },
                "activityLog": [
                    {
                        "action": "message_sent",
                        "timestamp": "2024-12-09T10:00:00Z"
                    }
                ],
                "location": {
                    "country": "US",
                    "timezone": "EST"
                },
                "timestamp": "2024-12-09T10:00:00Z"
            }
        }


# ============ UNIFY CONTEXT SCHEMAS ============

class UnifyContextRequest(BaseModel):
    """Schema for Unify workflow context data"""
    userId: str = Field(..., description="Unique user identifier")
    sessionId: str = Field(..., description="Session identifier")
    repoID: str = Field(..., description="Repository identifier")
    catalogID: str = Field(..., description="Source catalog (e.g., unify map)")
    ticketID: str = Field(..., description="Jira or ticket system ID")
    contextLevel: Literal["global", "project", "ticket"] = Field(..., description="Scope of context")
    AI_Client_type: List[str] = Field(..., description="AI tools involved (e.g., Claude, AWSQ, OpenCase)")
    details: str = Field(..., description="Natural language description of user action")
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


# ============ LEGACY SCHEMA (for backward compatibility) ============

class ContextRequest(BaseModel):
    """Legacy schema - kept for backward compatibility"""
    userId: str = Field(..., description="Unique user identifier")
    sessionId: str = Field(..., description="Session identifier")
    appContext: Optional[Dict[str, Any]] = Field(default={}, description="Application-specific context")
    conversationHistory: Optional[List[Dict[str, Any]]] = Field(default=[], description="Conversation messages")
    userPreferences: Optional[Dict[str, Any]] = Field(default={}, description="User preferences")
    deviceInfo: Optional[Dict[str, Any]] = Field(default={}, description="Device information")
    activityLog: Optional[List[Dict[str, Any]]] = Field(default=[], description="User activity log")
    location: Optional[Dict[str, str]] = Field(default={}, description="Location data")
    timestamp: datetime = Field(..., description="Event timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "userId": "user123",
                "sessionId": "session456",
                "appContext": {"appName": "MyApp", "version": "1.0.0"},
                "conversationHistory": [{"role": "user", "message": "Hello", "timestamp": "2024-12-09T10:00:00Z"}],
                "userPreferences": {"theme": "dark", "language": "en"},
                "deviceInfo": {"platform": "iOS", "deviceId": "device789"},
                "activityLog": [{"action": "login", "timestamp": "2024-12-09T09:00:00Z"}],
                "location": {"country": "US", "city": "San Francisco"},
                "timestamp": "2024-12-09T10:00:00Z"
            }
        }


# ============ RESPONSE SCHEMAS ============

class EnrichedContext(BaseModel):
    """Schema for enriched context data (Slack)"""
    summary: str
    keyTopics: List[str]
    userIntent: Optional[str] = None
    sentimentAnalysis: Optional[Dict[str, Any]] = None


class SlackContextResponse(BaseModel):
    """Schema for Slack API response"""
    status: str = Field(..., description="Response status")
    contextId: str = Field(..., description="Generated context ID")
    enrichedContext: Optional[EnrichedContext] = None
    recommendations: Optional[List[str]] = Field(default=[], description="AI recommendations")
    message: str = Field(..., description="Response message")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "contextId": "ctx_slack_abc123",
                "enrichedContext": {
                    "summary": "User asking about business hours",
                    "keyTopics": ["hours", "availability", "schedule"],
                    "userIntent": "information_request",
                    "sentimentAnalysis": {
                        "sentiment": "neutral",
                        "confidence": 0.85
                    }
                },
                "recommendations": [
                    "Provide business hours",
                    "Offer additional contact methods",
                    "Respond in en language"
                ],
                "message": "Slack context successfully stored and enriched"
            }
        }


class UnifyContextResponse(BaseModel):
    """Schema for Unify API response (per ContextPLTC spec)"""
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
                "userAlert": "AI agents are now aware of your authentication bug fix context",
                "file": {
                    "path": "src/auth/login.py",
                    "status": "tracked"
                },
                "message": "Unify workflow context successfully stored"
            }
        }


class ContextResponse(BaseModel):
    """Legacy schema for API response - kept for backward compatibility"""
    status: str = Field(..., description="Response status")
    contextId: str = Field(..., description="Generated context ID")
    enrichedContext: Optional[EnrichedContext] = None
    recommendations: Optional[List[str]] = Field(default=[], description="AI recommendations")
    message: str = Field(..., description="Response message")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "contextId": "ctx_abc123",
                "enrichedContext": {
                    "summary": "User initiated conversation about product features",
                    "keyTopics": ["features", "pricing", "support"],
                    "userIntent": "product_inquiry",
                    "sentimentAnalysis": {
                        "sentiment": "positive",
                        "confidence": 0.85
                    }
                },
                "recommendations": [
                    "Show pricing page",
                    "Offer demo",
                    "Connect with sales"
                ],
                "message": "Context successfully stored"
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
                "details": "userId is required"
            }
        }
