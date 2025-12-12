"""
FastAPI routes for Skills API (Context Artifact Type 1: Agent Profile Documents)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from api.schemas.skill_schema import (
    SkillResponse,
    SkillSearchResponse,
    SkillIngestionRequest,
    IngestionResponse
)
from api.services.skill_service import SkillService
from config.database import get_db


router = APIRouter(prefix="/api/skills", tags=["Skills API"])


@router.post(
    "/ingest",
    response_model=IngestionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Skills ingestion completed"},
        500: {"description": "Ingestion failed"}
    }
)
async def ingest_local_skills(db: Session = Depends(get_db)):
    """
    Ingest skills from local skills directory

    This endpoint:
    - Reads skill markdown files from the skills/ directory
    - Parses markdown content to extract title, description, category, tags
    - Stores skills in the database

    **Available Skills:**
    - doc-coauthoring, docx, frontend-design, mcp-builder, pdf, skill-creator,
      web-artifacts-builder, webapp-testing, xlsx, internal-comms, pptx

    **Response:**
    - status: Operation status
    - message: Summary message
    - skillsIngested: Number of skills successfully ingested
    - skillsSkipped: Number of skills skipped (already exist)
    - details: Array of detailed ingestion results
    """
    try:
        service = SkillService(db)
        result = service.ingest_local_skills()
        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Ingestion failed: {str(e)}"
            }
        )


@router.get(
    "",
    response_model=SkillSearchResponse,
    responses={
        200: {"description": "Skills retrieved successfully"}
    }
)
async def get_all_skills(
    limit: int = Query(50, ge=1, le=100, description="Maximum skills to return"),
    db: Session = Depends(get_db)
):
    """
    Get all agent skills/profiles

    Returns list of all ingested skills, ordered by most recent first.

    **Query Parameters:**
    - limit: Maximum results (1-100, default 50)

    **Response:**
    - status: Operation status
    - count: Number of skills returned
    - filters: Applied filters (empty for this endpoint)
    - data: Array of skill objects
    """
    try:
        service = SkillService(db)
        skills = service.get_all_skills(limit=limit)

        return SkillSearchResponse(
            status="success",
            count=len(skills),
            filters={},
            data=skills
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Failed to retrieve skills: {str(e)}"
            }
        )


@router.get(
    "/search",
    response_model=SkillSearchResponse,
    responses={
        200: {"description": "Search results retrieved successfully"}
    }
)
async def search_skills(
    query: Optional[str] = Query(None, description="Text search in title and description"),
    category: Optional[str] = Query(None, description="Filter by category (e.g., documentation, testing, design)"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results to return"),
    db: Session = Depends(get_db)
):
    """
    Search and filter agent skills

    This endpoint enables discovery of relevant agent skills by:
    - Text search in title and description
    - Category filtering (documentation, testing, design, development, etc.)
    - Tag filtering

    **Query Parameters:**
    - query: Text search (searches in title and description)
    - category: Category filter (documentation, testing, design, development, file-processing, web-development, communication, general)
    - tag: Tag filter
    - limit: Max results (1-100, default 20)

    **Example:**
    ```
    GET /api/skills/search?category=documentation&limit=10
    GET /api/skills/search?query=testing&tag=webapp
    ```

    **Response:**
    - status: Operation status
    - count: Number of results
    - filters: Applied search filters
    - data: Array of matching skills
    """
    try:
        service = SkillService(db)
        results = service.search_skills(
            query=query,
            category=category,
            tag=tag,
            limit=limit
        )

        return SkillSearchResponse(
            status="success",
            count=len(results),
            filters={
                "query": query,
                "category": category,
                "tag": tag
            },
            data=results
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Search failed: {str(e)}"
            }
        )


@router.get(
    "/{skill_id}",
    response_model=SkillResponse,
    responses={
        200: {"description": "Skill retrieved successfully"},
        404: {"description": "Skill not found"}
    }
)
async def get_skill(
    skill_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific skill by ID

    **Path Parameters:**
    - skill_id: Unique skill identifier (e.g., "doc-coauthoring", "webapp-testing")

    **Response:**
    - Skill object with full details including markdown content
    """
    try:
        service = SkillService(db)
        skill = service.get_skill(skill_id)

        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "status": "error",
                    "message": f"Skill {skill_id} not found"
                }
            )

        return skill

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Failed to retrieve skill: {str(e)}"
            }
        )


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Custom skill created successfully"},
        400: {"description": "Skill already exists or validation error"}
    }
)
async def create_custom_skill(
    skill_data: SkillIngestionRequest,
    db: Session = Depends(get_db)
):
    """
    Manually upload a custom skill

    This endpoint allows manual creation of custom agent skills/profiles
    for organization-specific use cases.

    **Request Body:**
    - skillId: Unique identifier (e.g., "custom-code-reviewer")
    - title: Skill title
    - description: Brief description (optional)
    - content: Full skill content in markdown format
    - category: Skill category (optional)
    - tags: Array of tags for searchability (optional)
    - source: Source system (default: "custom")
    - sourceUrl: Reference URL (optional)

    **Response:**
    - status: Operation status
    - message: Result message
    - data: Created skill object
    """
    try:
        service = SkillService(db)
        result = service.manual_ingest_skill(skill_data)

        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Failed to create skill: {str(e)}"
            }
        )
