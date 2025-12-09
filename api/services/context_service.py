"""
Business logic for Context API
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from api.models.context import UserContext, ContextAnalytics
from api.schemas.context_schema import ContextRequest, ContextResponse, EnrichedContext


class ContextService:
    """Service for handling context operations"""

    def __init__(self, db: Session):
        self.db = db

    def generate_context_id(self) -> str:
        """Generate a unique context ID"""
        return f"ctx_{uuid.uuid4().hex[:12]}"

    def enrich_context(self, context_data: ContextRequest) -> EnrichedContext:
        """
        Enrich the context with AI analysis

        In production, this would call an AI service for:
        - Summarization
        - Topic extraction
        - Intent detection
        - Sentiment analysis
        """
        # Simple mock enrichment - replace with actual AI service
        summary = f"User {context_data.userId} interaction in session {context_data.sessionId}"

        # Extract key topics from conversation history
        key_topics = []
        if context_data.conversationHistory:
            # In production, use NLP to extract topics
            key_topics = ["conversation", "interaction"]

        # Detect user intent
        user_intent = "general_inquiry"
        if context_data.conversationHistory:
            # In production, use intent classification model
            user_intent = "conversation_started"

        # Sentiment analysis
        sentiment_analysis = {
            "sentiment": "neutral",
            "confidence": 0.75
        }

        return EnrichedContext(
            summary=summary,
            keyTopics=key_topics,
            userIntent=user_intent,
            sentimentAnalysis=sentiment_analysis
        )

    def generate_recommendations(self, context_data: ContextRequest, enriched: EnrichedContext) -> list[str]:
        """
        Generate AI-powered recommendations

        In production, this would use ML models to provide contextual recommendations
        """
        recommendations = []

        # Mock recommendations based on context
        if enriched.userIntent == "conversation_started":
            recommendations.append("Greet the user warmly")
            recommendations.append("Ask how you can help")

        if context_data.userPreferences.get("language"):
            lang = context_data.userPreferences["language"]
            recommendations.append(f"Respond in {lang} language")

        return recommendations

    def store_context(self, context_data: ContextRequest) -> ContextResponse:
        """Store context data and return enriched response"""
        try:
            # Generate unique context ID
            context_id = self.generate_context_id()

            # Create context record
            user_context = UserContext(
                context_id=context_id,
                user_id=context_data.userId,
                session_id=context_data.sessionId,
                app_context=context_data.appContext or {},
                conversation_history=context_data.conversationHistory or [],
                user_preferences=context_data.userPreferences or {},
                device_info=context_data.deviceInfo or {},
                activity_log=context_data.activityLog or [],
                location=context_data.location or {},
                timestamp=context_data.timestamp
            )

            # Save to database
            self.db.add(user_context)
            self.db.commit()
            self.db.refresh(user_context)

            # Enrich context with AI analysis
            enriched_context = self.enrich_context(context_data)

            # Generate recommendations
            recommendations = self.generate_recommendations(context_data, enriched_context)

            # Log analytics event
            self._log_analytics_event(context_id, "context_stored", {
                "user_id": context_data.userId,
                "session_id": context_data.sessionId
            })

            return ContextResponse(
                status="success",
                contextId=context_id,
                enrichedContext=enriched_context,
                recommendations=recommendations,
                message="Context successfully stored and enriched"
            )

        except Exception as e:
            self.db.rollback()
            raise e

    def get_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve context by ID"""
        context = self.db.query(UserContext).filter(
            UserContext.context_id == context_id
        ).first()

        if context:
            return context.to_dict()
        return None

    def get_user_contexts(self, user_id: str, limit: int = 10) -> list[Dict[str, Any]]:
        """Retrieve recent contexts for a user"""
        contexts = self.db.query(UserContext).filter(
            UserContext.user_id == user_id
        ).order_by(UserContext.timestamp.desc()).limit(limit).all()

        return [ctx.to_dict() for ctx in contexts]

    def _log_analytics_event(self, context_id: str, event_type: str, event_data: Dict[str, Any]):
        """Log an analytics event"""
        try:
            analytics = ContextAnalytics(
                context_id=context_id,
                event_type=event_type,
                event_data=event_data
            )
            self.db.add(analytics)
            self.db.commit()
        except Exception as e:
            # Don't fail the main operation if analytics logging fails
            self.db.rollback()
            print(f"Analytics logging failed: {e}")
