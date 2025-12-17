"""
API routes for Context Plane Pre-Hook endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from config.database import get_db
from api.services.prehook_service import PreHookService
from api.schemas.skill_schema import (
    SkillUpdatesResponse,
    SkillSuggestionRequest,
    SkillSuggestionsResponse,
    SkillShareRequest,
    SkillShareResponse
)

router = APIRouter(prefix="/api/v1/skills", tags=["Pre-Hook Endpoints"])


@router.get("/updates", response_model=SkillUpdatesResponse)
async def check_skill_updates(
    user_id: str = Query(..., description="User identifier"),
    installed_skills: str = Query(..., description="JSON array of installed skills [{skill_id, version}]"),
    last_check: str = Query(..., description="ISO 8601 timestamp of last update check"),
    db: Session = Depends(get_db)
):
    """
    Check for skill updates and new skills since last session.

    Used by SessionStart hook to notify users of available updates.
    """
    import json

    # Parse installed_skills JSON
    try:
        installed_list = json.loads(installed_skills)
    except Exception:
        installed_list = []

    service = PreHookService(db)
    result = service.check_skill_updates(user_id, installed_list, last_check)

    return result


@router.post("/suggest", response_model=SkillSuggestionsResponse)
async def suggest_skills(
    request: SkillSuggestionRequest,
    db: Session = Depends(get_db)
):
    """
    Suggest relevant skills based on user prompt (v1 - keyword matching).

    Used during runtime to proactively offer skills when user describes a task.
    Future v2 will use semantic embeddings for better matching.
    """
    service = PreHookService(db)
    result = service.suggest_skills(request.userPrompt, request.context)

    return result


@router.post("/share", response_model=SkillShareResponse)
async def share_skill_modification(
    request: SkillShareRequest,
    db: Session = Depends(get_db)
):
    """
    Share a modified skill with team or organization.

    Used by SessionEnd hook when user makes improvements to a skill.
    """
    service = PreHookService(db)

    share_data = {
        "skillId": request.skillId,
        "baseVersion": request.baseVersion,
        "modifiedVersion": request.modifiedVersion,
        "changes": request.changes,
        "shareScope": request.shareScope,
        "teamId": request.teamId,
        "notifyUsers": request.notifyUsers
    }

    result = service.share_skill(share_data)

    return result


@router.post("/{skill_id}/install")
async def install_skill(
    skill_id: str,
    user_id: str = Query(..., description="User identifier"),
    db: Session = Depends(get_db)
):
    """
    Install a skill to the user's local ~/.claude/skills directory.

    This endpoint:
    - Fetches the skill content from the database
    - Writes the skill to ~/.claude/skills/{skill_id}.md
    - Updates ~/.claude/skills/installed_skills.json to track installed skills
    - Makes the skill available to Claude Code's Skill tool

    **Path Parameters:**
    - skill_id: The ID of the skill to install (e.g., "lucky-number", "predict-lucky-number")

    **Query Parameters:**
    - user_id: User identifier

    **Response:**
    - status: "success" or "error"
    - message: Human-readable result message
    - skillId: The installed skill ID
    - version: The installed version
    - installedPath: Path where skill was installed
    """
    service = PreHookService(db)
    result = service.install_skill(skill_id, user_id)

    return result
