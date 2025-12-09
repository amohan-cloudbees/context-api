"""
FastAPI routes for Context API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.schemas.context_schema import (
    ContextRequest, ContextResponse, ErrorResponse,
    SlackContextRequest, SlackContextResponse,
    UnifyContextRequest, UnifyContextResponse
)
from api.services.context_service import ContextService
from config.database import get_db

router = APIRouter(prefix="/api", tags=["Context API"])


@router.post(
    "/context",
    response_model=ContextResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Context successfully stored"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def store_context(
    context_data: ContextRequest,
    db: Session = Depends(get_db)
):
    """
    Store user context data and return enriched insights

    This endpoint receives context data from applications and:
    - Stores it in the database
    - Enriches it with AI analysis
    - Returns recommendations

    **Request Body:**
    - userId: Unique identifier for the user
    - sessionId: Session identifier
    - appContext: Application-specific context data
    - conversationHistory: Array of conversation messages
    - userPreferences: User preferences object
    - deviceInfo: Device information
    - activityLog: Array of user activities
    - location: Location data
    - timestamp: Event timestamp

    **Response:**
    - status: Operation status
    - contextId: Unique ID for this context
    - enrichedContext: AI-enriched context analysis
    - recommendations: AI-generated recommendations
    - message: Response message
    """
    try:
        service = ContextService(db)
        response = service.store_context(context_data)
        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status": "error", "error": "ValidationError", "details": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": "error", "error": "InternalServerError", "details": str(e)}
        )


@router.get(
    "/context/{context_id}",
    response_model=dict,
    responses={
        200: {"description": "Context retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Context not found"}
    }
)
async def get_context(
    context_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve stored context by ID

    **Path Parameters:**
    - context_id: The unique context identifier
    """
    try:
        service = ContextService(db)
        context = service.get_context(context_id)

        if not context:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"status": "error", "error": "NotFound", "details": f"Context {context_id} not found"}
            )

        return {"status": "success", "data": context}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": "error", "error": "InternalServerError", "details": str(e)}
        )


@router.get(
    "/contexts/user/{user_id}",
    response_model=dict,
    responses={
        200: {"description": "User contexts retrieved successfully"}
    }
)
async def get_user_contexts(
    user_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Retrieve recent contexts for a specific user

    **Path Parameters:**
    - user_id: The user identifier

    **Query Parameters:**
    - limit: Maximum number of contexts to return (default: 10)
    """
    try:
        service = ContextService(db)
        contexts = service.get_user_contexts(user_id, limit)

        return {
            "status": "success",
            "count": len(contexts),
            "data": contexts
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": "error", "error": "InternalServerError", "details": str(e)}
        )


@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Context API",
        "version": "1.0.0"
    }


# ============ SLACK CONTEXT ENDPOINTS ============

@router.post(
    "/context/slack",
    response_model=SlackContextResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Slack context successfully stored"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    tags=["Slack Context"]
)
async def store_slack_context(
    context_data: SlackContextRequest,
    db: Session = Depends(get_db)
):
    """
    Store Slack conversational context data

    This endpoint receives Slack bot conversation data and:
    - Stores it in the database
    - Enriches it with AI analysis (sentiment, intent, topics)
    - Returns recommendations for bot responses

    **Request Body:**
    - userId: Unique identifier for the user
    - sessionId: Session identifier (can be channel ID)
    - appContext: Slack-specific context (channel, thread, etc.)
    - conversationHistory: Array of conversation messages
    - userPreferences: User preferences (language, theme, etc.)
    - deviceInfo: Device/client information
    - activityLog: Array of user activities
    - location: Location/timezone data
    - timestamp: Event timestamp

    **Response:**
    - status: Operation status
    - contextId: Unique ID for this context
    - enrichedContext: AI-enriched analysis (summary, sentiment, intent, topics)
    - recommendations: AI-generated recommendations for bot responses
    - message: Response message
    """
    try:
        service = ContextService(db)
        response = service.store_slack_context(context_data)
        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status": "error", "error": "ValidationError", "details": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": "error", "error": "InternalServerError", "details": str(e)}
        )


# ============ UNIFY CONTEXT ENDPOINTS ============

@router.post(
    "/context/unify",
    response_model=UnifyContextResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Unify context successfully stored"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    tags=["Unify Context"]
)
async def store_unify_context(
    context_data: UnifyContextRequest,
    db: Session = Depends(get_db)
):
    """
    Store Unify workflow context data (per ContextPLTC specification)

    This endpoint receives Unify AI workflow context for code repositories, tickets, and AI agent coordination:
    - Stores workflow context in the database
    - Tracks files, repos, and tickets
    - Enables AI agents to access relevant context

    **Request Body:**
    - userId: Unique identifier for the developer/user
    - sessionId: Work session identifier
    - repoID: Repository identifier
    - catalogID: Source catalog (e.g., "unify_map")
    - ticketID: Jira or ticket system ID
    - contextLevel: Scope of context ("global", "project", or "ticket")
    - AI_Client_type: List of AI tools involved (e.g., ["Claude", "AWSQ", "OpenCase"])
    - details: Natural language description of the user's action/goal
    - files: Array of file references
    - timestamp: Event timestamp

    **Response:**
    - status: Operation status
    - contextId: Unique ID for this context
    - details: High-level status information
    - userAlert: User-facing alert message (if applicable)
    - file: File tracking information
    - message: Response message
    """
    try:
        service = ContextService(db)
        response = service.store_unify_context(context_data)
        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status": "error", "error": "ValidationError", "details": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": "error", "error": "InternalServerError", "details": str(e)}
        )
