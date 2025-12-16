"""
Script to generate embeddings for all skills in the database
Run this after adding new skills or to regenerate embeddings
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from config.database import SessionLocal
from api.models.skill import Skill
from api.services.embedding_service import EmbeddingService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_embeddings_for_all_skills(region_name: str = 'us-east-1'):
    """Generate embeddings for all skills that don't have them"""

    # Create database session
    db: Session = SessionLocal()

    try:
        # Initialize embedding service
        embedding_service = EmbeddingService(region_name=region_name)

        # Get all skills
        skills = db.query(Skill).all()
        logger.info(f"Found {len(skills)} skills in database")

        success_count = 0
        skip_count = 0
        error_count = 0

        for skill in skills:
            # Skip if embedding already exists
            if skill.embedding:
                logger.info(f"Skipping {skill.skill_id} - embedding already exists")
                skip_count += 1
                continue

            logger.info(f"Generating embedding for: {skill.skill_id}")

            # Generate embedding
            embedding = embedding_service.generate_skill_embedding(
                skill.title,
                skill.description or "",
                skill.tags or []
            )

            if embedding:
                # Store embedding as JSON array
                skill.embedding = embedding
                success_count += 1
                logger.info(f"✓ Generated embedding for {skill.skill_id} ({len(embedding)} dimensions)")
            else:
                error_count += 1
                logger.error(f"✗ Failed to generate embedding for {skill.skill_id}")

        # Commit changes
        db.commit()

        logger.info(f"""
        ========================================
        Embedding Generation Complete
        ========================================
        Total skills: {len(skills)}
        Success: {success_count}
        Skipped (already have embeddings): {skip_count}
        Errors: {error_count}
        ========================================
        """)

    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    # You can pass AWS region as argument
    region = sys.argv[1] if len(sys.argv) > 1 else 'us-east-1'
    logger.info(f"Using AWS region: {region}")

    generate_embeddings_for_all_skills(region_name=region)
