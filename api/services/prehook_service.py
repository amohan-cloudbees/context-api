"""
Service for Context Plane Pre-Hook endpoints
Handles skill updates, suggestions, and sharing
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from api.models.skill import Skill
from api.models.user_skill import UserSkill
from datetime import datetime
from typing import List, Dict, Optional
import re


class PreHookService:
    """Service for pre-hook operations"""

    def __init__(self, db: Session):
        self.db = db

    def check_skill_updates(self, user_id: str, installed_skills: List[Dict], last_check: str):
        """
        Check for skill updates and new skills

        Args:
            user_id: User identifier
            installed_skills: List of {skill_id, version} dicts
            last_check: ISO 8601 timestamp of last check

        Returns:
            Dict with available_updates and new_skills lists
        """
        # Convert installed skills to dict for easy lookup
        installed_map = {skill['skill_id']: skill['version'] for skill in installed_skills}

        # Get all available skills
        all_skills = self.db.query(Skill).all()

        available_updates = []
        new_skills = []

        for skill in all_skills:
            if skill.skill_id in installed_map:
                # Check if there's an update
                current_version = installed_map[skill.skill_id]
                if self._compare_versions(skill.version, current_version) > 0:
                    available_updates.append({
                        "skillId": skill.skill_id,
                        "name": skill.title,
                        "currentVersion": current_version,
                        "latestVersion": skill.version,
                        "category": skill.category or "general",
                        "description": skill.description or "",
                        "changelogUrl": skill.changelog_url,
                        "installUrl": skill.install_url,
                        "usageCount": skill.usage_count or 0,
                        "maintainer": skill.maintainer or "unknown"
                    })
            else:
                # This is a new skill the user doesn't have
                # Check if skill was created after last_check
                try:
                    last_check_dt = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
                    if skill.created_at and skill.created_at > last_check_dt:
                        new_skills.append({
                            "skillId": skill.skill_id,
                            "name": skill.title,
                            "currentVersion": "0.0.0",
                            "latestVersion": skill.version,
                            "category": skill.category or "general",
                            "description": skill.description or "",
                            "changelogUrl": skill.changelog_url,
                            "installUrl": skill.install_url,
                            "usageCount": skill.usage_count or 0,
                            "maintainer": skill.maintainer or "unknown"
                        })
                except Exception:
                    # If date parsing fails, include as new skill
                    new_skills.append({
                        "skillId": skill.skill_id,
                        "name": skill.title,
                        "currentVersion": "0.0.0",
                        "latestVersion": skill.version,
                        "category": skill.category or "general",
                        "description": skill.description or "",
                        "changelogUrl": skill.changelog_url,
                        "installUrl": skill.install_url,
                        "usageCount": skill.usage_count or 0,
                        "maintainer": skill.maintainer or "unknown"
                    })

        return {
            "availableUpdates": available_updates,
            "newSkills": new_skills
        }

    def suggest_skills(self, user_prompt: str, context: Optional[Dict] = None):
        """
        Suggest relevant skills based on user prompt (v1 - keyword matching)

        Args:
            user_prompt: User's task description
            context: Additional context (files, repo, project type)

        Returns:
            Dict with suggestions list
        """
        # Get all skills
        all_skills = self.db.query(Skill).all()

        # Simple keyword matching (v1)
        suggestions = []

        # Extract keywords from prompt
        prompt_lower = user_prompt.lower()
        prompt_keywords = set(re.findall(r'\w+', prompt_lower))

        for skill in all_skills:
            confidence = self._calculate_keyword_confidence(
                prompt_keywords,
                skill
            )

            if confidence > 0.3:  # Threshold for suggestion
                suggestions.append({
                    "skillId": skill.skill_id,
                    "confidence": round(confidence, 2),
                    "reasoning": self._generate_reasoning(prompt_keywords, skill),
                    "skillMetadata": {
                        "name": skill.title,
                        "description": skill.description or "",
                        "category": skill.category or "general",
                        "capabilities": skill.tags or []
                    }
                })

        # Sort by confidence descending
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)

        # Return top 3 suggestions
        return {
            "suggestions": suggestions[:3]
        }

    def share_skill(self, share_data: Dict):
        """
        Share a modified skill with team/organization

        Args:
            share_data: Dict with skillId, versions, changes, scope, etc.

        Returns:
            Dict with status and share info
        """
        skill_id = share_data['skillId']
        modified_version = share_data['modifiedVersion']
        share_scope = share_data['shareScope']
        team_id = share_data.get('teamId')

        # Find the base skill
        base_skill = self.db.query(Skill).filter(
            Skill.skill_id == skill_id
        ).first()

        if not base_skill:
            return {
                "status": "error",
                "message": f"Skill {skill_id} not found",
                "sharedSkillId": "",
                "shareUrl": "",
                "notifiedUsers": 0
            }

        # Create a new skill entry for the modified version
        new_skill_id = f"{skill_id}-{share_scope}"
        if team_id:
            new_skill_id = f"{skill_id}-{team_id}"

        # Check if modified version already exists
        existing = self.db.query(Skill).filter(
            Skill.skill_id == new_skill_id
        ).first()

        if existing:
            # Update existing
            existing.version = modified_version
            existing.content = share_data['changes'].get('changelog', existing.content)
            existing.updated_at = datetime.utcnow()
        else:
            # Create new skill entry
            new_skill = Skill(
                skill_id=new_skill_id,
                title=f"{base_skill.title} ({share_scope})",
                description=base_skill.description,
                content=base_skill.content + "\n\n## Modifications\n" + share_data['changes'].get('changelog', ''),
                category=base_skill.category,
                tags=base_skill.tags,
                source='custom',
                version=modified_version,
                visibility_scope=share_scope,
                maintainer=team_id or 'user-contributed'
            )
            self.db.add(new_skill)

        self.db.commit()

        # Calculate notified users (mock for demo)
        notified_count = 0
        if share_scope == "team":
            notified_count = 12  # Mock value
        elif share_scope == "organization":
            notified_count = 247  # Mock value

        return {
            "status": "success",
            "message": "Skill modification shared successfully",
            "sharedSkillId": new_skill_id,
            "shareUrl": f"https://example.com/skills/{new_skill_id}",
            "notifiedUsers": notified_count
        }

    def _compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two semantic versions
        Returns: 1 if version1 > version2, -1 if version1 < version2, 0 if equal
        """
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]

            # Pad shorter version with zeros
            while len(v1_parts) < len(v2_parts):
                v1_parts.append(0)
            while len(v2_parts) < len(v1_parts):
                v2_parts.append(0)

            for i in range(len(v1_parts)):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1

            return 0
        except Exception:
            return 0

    def _calculate_keyword_confidence(self, prompt_keywords: set, skill: Skill) -> float:
        """Calculate confidence score based on keyword matching"""
        skill_text = f"{skill.title} {skill.description or ''} {' '.join(skill.tags or [])}".lower()
        skill_keywords = set(re.findall(r'\w+', skill_text))

        # Calculate overlap
        common_keywords = prompt_keywords.intersection(skill_keywords)

        if not prompt_keywords:
            return 0.0

        # Base score from keyword overlap
        overlap_score = len(common_keywords) / len(prompt_keywords)

        # Boost if title matches
        title_keywords = set(re.findall(r'\w+', skill.title.lower()))
        title_overlap = len(prompt_keywords.intersection(title_keywords))
        if title_overlap > 0:
            overlap_score += 0.2

        # Boost if category matches
        if skill.category:
            category_keywords = set(re.findall(r'\w+', skill.category.lower()))
            if prompt_keywords.intersection(category_keywords):
                overlap_score += 0.1

        return min(overlap_score, 1.0)

    def _generate_reasoning(self, prompt_keywords: set, skill: Skill) -> str:
        """Generate human-readable reasoning for the suggestion"""
        skill_text = f"{skill.title} {skill.description or ''}".lower()
        skill_keywords = set(re.findall(r'\w+', skill_text))

        common_keywords = prompt_keywords.intersection(skill_keywords)

        if common_keywords:
            keywords_str = ', '.join(list(common_keywords)[:3])
            return f"User prompt mentions keywords that match this skill: {keywords_str}"

        return "This skill may be relevant to the user's task"
