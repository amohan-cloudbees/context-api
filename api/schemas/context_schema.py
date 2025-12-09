"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class ContextRequest(BaseModel):
    """Schema for incoming context data"""
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
                    "appName": "MyApp",
                    "version": "1.0.0"
                },
                "conversationHistory": [
                    {
                        "role": "user",
                        "message": "Hello",
                        "timestamp": "2024-12-09T10:00:00Z"
                    }
                ],
                "userPreferences": {
                    "theme": "dark",
                    "language": "en"
                },
                "deviceInfo": {
                    "platform": "iOS",
                    "deviceId": "device789"
                },
                "activityLog": [
                    {
                        "action": "login",
                        "timestamp": "2024-12-09T09:00:00Z"
                    }
                ],
                "location": {
                    "country": "US",
                    "city": "San Francisco"
                },
                "timestamp": "2024-12-09T10:00:00Z"
            }
        }


class EnrichedContext(BaseModel):
    """Schema for enriched context data"""
    summary: str
    keyTopics: List[str]
    userIntent: Optional[str] = None
    sentimentAnalysis: Optional[Dict[str, Any]] = None


class ContextResponse(BaseModel):
    """Schema for API response"""
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
