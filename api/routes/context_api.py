"""
FastAPI routes for Context API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from api.schemas.context_schema import ContextRequest, ContextResponse, ErrorResponse
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
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "bug_fix": {
                            "summary": "Bug Fix in Progress",
                            "description": "Developer working on authentication bug with AI help",
                            "value": {
                                "userId": "developer123",
                                "sessionId": "work_session_456",
                                "repoID": "repo_abc123",
                                "catalogID": "unify_map",
                                "ticketID": "JIRA-1234",
                                "contextLevel": "ticket",
                                "AI_Client_type": ["Claude", "AWSQ"],
                                "details": "I am trying to fix the authentication bug in the login module",
                                "files": [{"path": "src/auth/login.py", "type": "python", "action": "modified"}],
                                "conversationHistory": [
                                    {"role": "user", "aiClient": "Claude", "message": "Can you help me debug the authentication issue?", "timestamp": "2024-12-09T09:55:00Z"},
                                    {"role": "assistant", "aiClient": "Claude", "message": "I'll help you investigate the login.py file.", "timestamp": "2024-12-09T09:56:00Z"}
                                ],
                                "status": "in_progress",
                                "blockedBy": None,
                                "timestamp": "2024-12-09T10:00:00Z"
                            }
                        },
                        "blocked_work": {
                            "summary": "Blocked Work",
                            "description": "Work blocked by dependency on another ticket",
                            "value": {
                                "userId": "jane_dev",
                                "sessionId": "session_789",
                                "repoID": "unify_backend",
                                "catalogID": "unify_map",
                                "ticketID": "JIRA-5678",
                                "contextLevel": "ticket",
                                "AI_Client_type": ["AWSQ"],
                                "details": "Cannot implement new API endpoint until database schema is updated",
                                "files": [{"path": "api/routes/users.go", "type": "go", "action": "created"}],
                                "conversationHistory": [
                                    {"role": "user", "aiClient": "AWSQ", "message": "I need to create the /users endpoint but the schema isn't ready", "timestamp": "2024-12-11T14:00:00Z"},
                                    {"role": "assistant", "aiClient": "AWSQ", "message": "I see JIRA-4567 handles the schema migration. Let me mark this as blocked.", "timestamp": "2024-12-11T14:01:00Z"}
                                ],
                                "status": "blocked",
                                "blockedBy": "JIRA-4567",
                                "timestamp": "2024-12-11T14:05:00Z"
                            }
                        },
                        "new_feature": {
                            "summary": "New Feature Development",
                            "description": "Starting fresh feature with multiple files",
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
                                    {"path": "src/components/Dashboard.tsx", "type": "typescript", "action": "created"},
                                    {"path": "src/api/metrics.ts", "type": "typescript", "action": "created"}
                                ],
                                "conversationHistory": [
                                    {"role": "user", "aiClient": "Claude", "message": "Help me design a dashboard component that shows real-time system metrics", "timestamp": "2024-12-11T10:00:00Z"},
                                    {"role": "assistant", "aiClient": "Claude", "message": "I'll help you create a React dashboard with chart components.", "timestamp": "2024-12-11T10:01:00Z"}
                                ],
                                "status": "in_progress",
                                "blockedBy": None,
                                "timestamp": "2024-12-11T10:30:00Z"
                            }
                        },
                        "code_review": {
                            "summary": "Code Review Context",
                            "description": "Context for completed work awaiting review",
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
                                    {"path": "services/user_service.py", "type": "python", "action": "modified"},
                                    {"path": "cache/redis_client.py", "type": "python", "action": "created"}
                                ],
                                "conversationHistory": [
                                    {"role": "user", "aiClient": "Claude", "message": "I've implemented Redis caching. Can you review the code?", "timestamp": "2024-12-11T16:00:00Z"}
                                ],
                                "status": "needs_review",
                                "blockedBy": None,
                                "timestamp": "2024-12-11T16:10:00Z"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def store_context(
    context_data: ContextRequest,
    db: Session = Depends(get_db)
):
    """
    Store workflow context data (per ContextPLTC specification)

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


@router.get(
    "/contexts/search",
    response_model=dict,
    responses={
        200: {"description": "Search results retrieved successfully"}
    },
    tags=["Context Discovery"]
)
async def search_contexts(
    repoID: Optional[str] = Query(None, description="Filter by repository ID"),
    ticketID: Optional[str] = Query(None, description="Filter by ticket ID"),
    filePath: Optional[str] = Query(None, description="Search by file path (partial match)"),
    contextLevel: Optional[str] = Query(None, description="Filter by context level (global/project/ticket)"),
    aiClient: Optional[str] = Query(None, description="Filter by AI client type"),
    status: Optional[str] = Query(None, description="Filter by workflow status (not_started/in_progress/blocked/needs_review/completed)"),
    query: Optional[str] = Query(None, description="Text search in details field"),
    limit: int = Query(10, ge=1, le=100, description="Maximum results to return"),
    db: Session = Depends(get_db)
):
    """
    Search and discover contexts with flexible filtering

    This endpoint enables AI agents to find relevant context by:
    - Repository or ticket
    - File paths
    - Context level
    - AI client type
    - Workflow status
    - Natural language query in details

    **Query Parameters:**
    - repoID: Repository identifier
    - ticketID: Ticket identifier
    - filePath: File path (supports partial matching)
    - contextLevel: Scope filter (global, project, ticket)
    - aiClient: AI client filter (Claude, AWSQ, etc.)
    - status: Workflow status filter (not_started, in_progress, blocked, needs_review, completed)
    - query: Text search in details field
    - limit: Max results (1-100, default 10)

    **Example:**
    ```
    GET /api/contexts/search?repoID=repo_abc123&status=in_progress&limit=5
    ```
    """
    try:
        service = ContextService(db)
        results = service.search_contexts(
            repo_id=repoID,
            ticket_id=ticketID,
            file_path=filePath,
            context_level=contextLevel,
            ai_client=aiClient,
            query_text=query,
            status=status,
            limit=limit
        )

        return {
            "status": "success",
            "count": len(results),
            "filters": {
                "repoID": repoID,
                "ticketID": ticketID,
                "filePath": filePath,
                "contextLevel": contextLevel,
                "aiClient": aiClient,
                "status": status,
                "query": query
            },
            "data": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": "error", "error": "InternalServerError", "details": str(e)}
        )


@router.get(
    "/contexts/repo/{repo_id}",
    response_model=dict,
    responses={
        200: {"description": "Repository contexts retrieved successfully"}
    },
    tags=["Context Discovery"]
)
async def get_repo_contexts(
    repo_id: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all contexts for a specific repository

    **Path Parameters:**
    - repo_id: Repository identifier

    **Query Parameters:**
    - limit: Maximum results (default 20)
    """
    try:
        service = ContextService(db)
        contexts = service.get_contexts_by_repo(repo_id, limit)

        return {
            "status": "success",
            "repoID": repo_id,
            "count": len(contexts),
            "data": contexts
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": "error", "error": "InternalServerError", "details": str(e)}
        )


@router.get(
    "/contexts/ticket/{ticket_id}",
    response_model=dict,
    responses={
        200: {"description": "Ticket contexts retrieved successfully"}
    },
    tags=["Context Discovery"]
)
async def get_ticket_contexts(
    ticket_id: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all contexts for a specific ticket

    **Path Parameters:**
    - ticket_id: Ticket identifier (e.g., JIRA-1234)

    **Query Parameters:**
    - limit: Maximum results (default 20)
    """
    try:
        service = ContextService(db)
        contexts = service.get_contexts_by_ticket(ticket_id, limit)

        return {
            "status": "success",
            "ticketID": ticket_id,
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
