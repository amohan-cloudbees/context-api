"""
Service for generating embeddings using AWS Bedrock Titan
"""
import boto3
import json
import numpy as np
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using AWS Bedrock Titan"""

    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize Bedrock client

        Args:
            region_name: AWS region for Bedrock service
        """
        try:
            self.bedrock_runtime = boto3.client(
                'bedrock-runtime',
                region_name=region_name
            )
            self.model_id = 'amazon.titan-embed-text-v2:0'
            logger.info(f"Bedrock Embedding Service initialized with model: {self.model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            self.bedrock_runtime = None

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for given text

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector (1024 dimensions)
            or None if generation fails
        """
        if not self.bedrock_runtime:
            logger.error("Bedrock client not initialized")
            return None

        try:
            # Prepare request body
            request_body = {
                "inputText": text
            }

            # Invoke Bedrock model
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )

            # Parse response
            response_body = json.loads(response['body'].read())
            embedding = response_body.get('embedding')

            if embedding:
                logger.debug(f"Generated embedding of dimension: {len(embedding)}")
                return embedding
            else:
                logger.error("No embedding in response")
                return None

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def generate_skill_embedding(self, skill_title: str, skill_description: str, skill_tags: List[str]) -> Optional[List[float]]:
        """
        Generate embedding for a skill based on its metadata

        Args:
            skill_title: Skill title
            skill_description: Skill description
            skill_tags: List of skill tags

        Returns:
            Embedding vector or None if generation fails
        """
        # Combine skill metadata into a single text for embedding
        text_parts = [skill_title]

        if skill_description:
            text_parts.append(skill_description)

        if skill_tags:
            text_parts.append(" ".join(skill_tags))

        combined_text = " ".join(text_parts)

        return self.generate_embedding(combined_text)

    @staticmethod
    def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embedding vectors

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score between -1 and 1
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return float(similarity)

        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0

    def find_most_similar(self, query_embedding: List[float], skill_embeddings: List[tuple]) -> List[tuple]:
        """
        Find most similar skills based on embedding similarity

        Args:
            query_embedding: Query embedding vector
            skill_embeddings: List of (skill, embedding) tuples

        Returns:
            List of (skill, similarity_score) tuples sorted by similarity descending
        """
        results = []

        for skill, embedding in skill_embeddings:
            if embedding:
                similarity = self.cosine_similarity(query_embedding, embedding)
                results.append((skill, similarity))

        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)

        return results
