"""
Business logic for Skills API (Context Artifact Type 1: Agent Profile Documents)
"""
import re
import requests
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from api.models.skill import Skill
from api.schemas.skill_schema import SkillIngestionRequest, IngestionResponse


class SkillService:
    """Service for handling skills/agent profiles operations"""

    # Skills to include (engineering-related)
    INCLUDED_SKILLS = {
        'doc-coauthoring', 'docx', 'frontend-design', 'mcp-builder',
        'pdf', 'skill-creator', 'web-artifacts-builder', 'webapp-testing',
        'xlsx', 'internal-comms', 'pptx'
    }

    # Skills to exclude (creative/non-engineering)
    EXCLUDED_SKILLS = {
        'algorithmic-art', 'brand-guidelines', 'canvas-design',
        'slack-gif-creator', 'theme-factory'
    }

    def __init__(self, db: Session):
        self.db = db
        self.github_api = "https://api.github.com"
        self.skills_repo = "anthropics/skills"

    def should_ingest_skill(self, skill_name: str) -> bool:
        """
        Determine if a skill should be ingested based on engineering relevance

        Returns True if skill is engineering-related, False otherwise
        """
        return skill_name in self.INCLUDED_SKILLS

    def fetch_anthropic_skills(self) -> List[Dict[str, Any]]:
        """
        Fetch list of skills from Anthropic's skills GitHub repository

        Returns list of skill directories from the repo
        """
        url = f"{self.github_api}/repos/{self.skills_repo}/contents/skills"

        try:
            response = requests.get(url)
            response.raise_for_status()

            contents = response.json()

            # Filter to only directories (actual skills)
            skill_dirs = [
                item for item in contents
                if item['type'] == 'dir' and self.should_ingest_skill(item['name'])
            ]

            return skill_dirs

        except requests.RequestException as e:
            raise Exception(f"Failed to fetch skills from GitHub: {str(e)}")

    def fetch_skill_markdown(self, skill_name: str) -> str:
        """
        Fetch the SKILL.md content for a specific skill

        Args:
            skill_name: Name of the skill directory

        Returns:
            Markdown content as string
        """
        url = f"{self.github_api}/repos/{self.skills_repo}/contents/skills/{skill_name}/SKILL.md"

        try:
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            # GitHub API returns base64 encoded content
            import base64
            content = base64.b64decode(data['content']).decode('utf-8')

            return content

        except requests.RequestException as e:
            raise Exception(f"Failed to fetch skill.md for {skill_name}: {str(e)}")

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

    def ingest_anthropic_skills(self) -> IngestionResponse:
        """
        Main ingestion method: Fetch and store all Anthropic skills

        This orchestrates the full ingestion process:
        1. Fetch skill list from GitHub
        2. For each skill, fetch its markdown content
        3. Parse the markdown
        4. Filter based on engineering relevance
        5. Store in database

        Returns:
            IngestionResponse with statistics and details
        """
        ingested_count = 0
        skipped_count = 0
        details = []

        try:
            # Fetch list of skills from GitHub
            skill_dirs = self.fetch_anthropic_skills()

            # Process each skill
            for skill_dir in skill_dirs:
                skill_name = skill_dir['name']

                try:
                    # Fetch markdown content
                    markdown_content = self.fetch_skill_markdown(skill_name)

                    # Parse skill data
                    skill_data = self.parse_skill_markdown(markdown_content, skill_name)

                    # Generate source URL
                    source_url = f"https://github.com/{self.skills_repo}/tree/main/skills/{skill_name}"

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

            # Add info about excluded skills
            for excluded in self.EXCLUDED_SKILLS:
                details.append(f"Filtered out: {excluded} (not engineering-related)")

            return IngestionResponse(
                status="success",
                message=f"Successfully ingested {ingested_count} skills from Anthropic repository",
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
