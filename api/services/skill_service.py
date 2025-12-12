"""
Business logic for Skills API (Context Artifact Type 1: Agent Profile Documents)
"""
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from api.models.skill import Skill
from api.schemas.skill_schema import SkillIngestionRequest, IngestionResponse


class SkillService:
    """Service for handling skills/agent profiles operations"""

    def __init__(self, db: Session):
        self.db = db
        # Path to local skills directory
        self.skills_dir = Path(__file__).parent.parent.parent / "skills"

    def get_local_skills(self) -> List[str]:
        """
        Get list of skills from local skills directory

        Returns list of skill names (without .md extension)
        """
        if not self.skills_dir.exists():
            raise Exception(f"Skills directory not found: {self.skills_dir}")

        skill_files = []
        for file_path in self.skills_dir.glob("*.md"):
            skill_files.append(file_path.stem)  # Get filename without extension

        return skill_files

    def read_skill_markdown(self, skill_name: str) -> str:
        """
        Read skill markdown content from local file

        Args:
            skill_name: Name of the skill (without .md extension)

        Returns:
            Markdown content as string
        """
        skill_file = self.skills_dir / f"{skill_name}.md"

        if not skill_file.exists():
            raise Exception(f"Skill file not found: {skill_file}")

        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to read skill file {skill_name}: {str(e)}")

    def parse_skill_markdown(self, markdown_content: str, skill_id: str) -> Dict[str, Any]:
        """
        Parse skill markdown to extract title, description, category, and tags

        Args:
            markdown_content: Raw markdown content
            skill_id: Skill identifier

        Returns:
            Dictionary with parsed skill data
        """
        lines = markdown_content.strip().split('\n')

        # Extract title (first heading)
        title = skill_id.replace('-', ' ').title()
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break

        # Extract description (first paragraph after title)
        description = None
        in_content = False
        for i, line in enumerate(lines):
            if line.startswith('# '):
                in_content = True
                continue
            if in_content and line.strip() and not line.startswith('#'):
                description = line.strip()
                break

        # Determine category based on skill name patterns
        category = self._categorize_skill(skill_id, markdown_content)

        # Extract tags from skill name and content
        tags = self._extract_tags(skill_id, markdown_content)

        return {
            'skill_id': skill_id,
            'title': title,
            'description': description or f"Agent profile for {title}",
            'content': markdown_content,
            'category': category,
            'tags': tags
        }

    def _categorize_skill(self, skill_id: str, content: str) -> str:
        """
        Categorize skill based on its name and content

        Returns category string like 'documentation', 'testing', 'design', etc.
        """
        content_lower = content.lower()

        if 'doc' in skill_id or 'documentation' in content_lower:
            return 'documentation'
        elif 'test' in skill_id or 'testing' in content_lower:
            return 'testing'
        elif 'design' in skill_id or 'frontend' in skill_id:
            return 'design'
        elif 'mcp' in skill_id or 'builder' in skill_id:
            return 'development'
        elif 'pdf' in skill_id or 'xlsx' in skill_id or 'pptx' in skill_id or 'docx' in skill_id:
            return 'file-processing'
        elif 'web' in skill_id or 'webapp' in skill_id:
            return 'web-development'
        elif 'comms' in skill_id or 'communication' in content_lower:
            return 'communication'
        else:
            return 'general'

    def _extract_tags(self, skill_id: str, content: str) -> List[str]:
        """
        Extract relevant tags from skill ID and content

        Returns list of tags for searchability
        """
        tags = []

        # Add skill name parts as tags
        tags.extend(skill_id.split('-'))

        # Add common keywords if found in content
        keywords = ['documentation', 'testing', 'design', 'frontend', 'backend',
                   'api', 'database', 'deployment', 'CI/CD', 'security', 'performance']

        content_lower = content.lower()
        for keyword in keywords:
            if keyword in content_lower:
                tags.append(keyword)

        # Remove duplicates and return
        return list(set(tags))

    def ingest_skill(self, skill_data: Dict[str, Any], source_url: str) -> bool:
        """
        Store a single skill in the database

        Args:
            skill_data: Parsed skill data dictionary
            source_url: GitHub URL for the skill

        Returns:
            True if ingested successfully, False if skipped (already exists)
        """
        try:
            skill = Skill(
                skill_id=skill_data['skill_id'],
                title=skill_data['title'],
                description=skill_data['description'],
                content=skill_data['content'],
                category=skill_data['category'],
                tags=skill_data['tags'],
                source='anthropic',
                source_url=source_url
            )

            self.db.add(skill)
            self.db.commit()
            self.db.refresh(skill)

            return True

        except IntegrityError:
            # Skill already exists (duplicate skill_id)
            self.db.rollback()
            return False
        except Exception as e:
            self.db.rollback()
            raise e

    def ingest_local_skills(self) -> IngestionResponse:
        """
        Main ingestion method: Load and store all skills from local directory

        This orchestrates the full ingestion process:
        1. Get skill list from local skills/ directory
        2. For each skill, read its markdown content
        3. Parse the markdown
        4. Store in database

        Returns:
            IngestionResponse with statistics and details
        """
        ingested_count = 0
        skipped_count = 0
        details = []

        try:
            # Get list of skills from local directory
            skill_names = self.get_local_skills()

            # Process each skill
            for skill_name in skill_names:
                try:
                    # Read markdown content
                    markdown_content = self.read_skill_markdown(skill_name)

                    # Parse skill data
                    skill_data = self.parse_skill_markdown(markdown_content, skill_name)

                    # Generate source URL
                    source_url = f"https://github.com/anthropics/skills/tree/main/skills/{skill_name}"

                    # Ingest skill
                    if self.ingest_skill(skill_data, source_url):
                        ingested_count += 1
                        details.append(f"Ingested: {skill_name}")
                    else:
                        skipped_count += 1
                        details.append(f"Skipped: {skill_name} (already exists)")

                except Exception as e:
                    skipped_count += 1
                    details.append(f"Failed: {skill_name} - {str(e)}")

            return IngestionResponse(
                status="success",
                message=f"Successfully ingested {ingested_count} skills from local directory",
                skillsIngested=ingested_count,
                skillsSkipped=skipped_count,
                details=details
            )

        except Exception as e:
            return IngestionResponse(
                status="error",
                message=f"Ingestion failed: {str(e)}",
                skillsIngested=ingested_count,
                skillsSkipped=skipped_count,
                details=details
            )

    def get_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single skill by ID"""
        skill = self.db.query(Skill).filter(Skill.skill_id == skill_id).first()

        if skill:
            return skill.to_dict()
        return None

    def get_all_skills(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve all skills with optional limit"""
        skills = self.db.query(Skill).order_by(
            Skill.created_at.desc()
        ).limit(limit).all()

        return [skill.to_dict() for skill in skills]

    def search_skills(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search skills with flexible filtering

        Args:
            query: Text search in title and description
            category: Filter by category
            tag: Filter by tag
            limit: Maximum results to return

        Returns:
            List of matching skills
        """
        query_obj = self.db.query(Skill)

        # Text search in title and description
        if query:
            query_obj = query_obj.filter(
                (Skill.title.ilike(f'%{query}%')) |
                (Skill.description.ilike(f'%{query}%'))
            )

        # Filter by category
        if category:
            query_obj = query_obj.filter(Skill.category == category)

        # Filter by tag (check if tag exists in tags array)
        if tag:
            query_obj = query_obj.filter(Skill.tags.any(tag))

        # Order by most recent and limit
        skills = query_obj.order_by(
            Skill.created_at.desc()
        ).limit(limit).all()

        return [skill.to_dict() for skill in skills]

    def manual_ingest_skill(self, skill_request: SkillIngestionRequest) -> Dict[str, Any]:
        """
        Manually ingest a custom skill (for future custom skills)

        Args:
            skill_request: SkillIngestionRequest with skill data

        Returns:
            Dictionary with ingestion result
        """
        try:
            skill = Skill(
                skill_id=skill_request.skillId,
                title=skill_request.title,
                description=skill_request.description,
                content=skill_request.content,
                category=skill_request.category,
                tags=skill_request.tags or [],
                source=skill_request.source,
                source_url=skill_request.sourceUrl
            )

            self.db.add(skill)
            self.db.commit()
            self.db.refresh(skill)

            return {
                "status": "success",
                "message": f"Skill {skill_request.skillId} ingested successfully",
                "data": skill.to_dict()
            }

        except IntegrityError:
            self.db.rollback()
            return {
                "status": "error",
                "message": f"Skill {skill_request.skillId} already exists",
                "data": None
            }
        except Exception as e:
            self.db.rollback()
            raise e
