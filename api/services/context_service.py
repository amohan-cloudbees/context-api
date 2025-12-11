"""
Business logic for Context API
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from api.models.context import UserContext, ContextAnalytics
from api.schemas.context_schema import ContextRequest, ContextResponse


class ContextService:
    """Service for handling workflow context operations"""

    def __init__(self, db: Session):
        self.db = db

    def generate_context_id(self) -> str:
        """Generate a unique context ID"""
        return f"ctx_{uuid.uuid4().hex[:12]}"

    def store_context(self, context_data: ContextRequest) -> ContextResponse:
        """Store workflow context data (per ContextPLTC spec)"""
        try:
            # Generate unique context ID
            context_id = self.generate_context_id()

            # Prepare context_data JSONB
            context_json = {
                "repoID": context_data.repoID,
                "catalogID": context_data.catalogID,
                "ticketID": context_data.ticketID,
                "contextLevel": context_data.contextLevel,
                "AI_Client_type": context_data.AI_Client_type,
                "details": context_data.details,
                "files": context_data.files or []
            }

            # Create context record
            user_context = UserContext(
                context_id=context_id,
                user_id=context_data.userId,
                session_id=context_data.sessionId,
                context_data=context_json,
                timestamp=context_data.timestamp
            )

            # Save to database
            self.db.add(user_context)
            self.db.commit()
            self.db.refresh(user_context)

            # Generate response per ContextPLTC spec
            details = f"Context captured for ticket {context_data.ticketID} in repo {context_data.repoID}"

            # Check for alerts (mock logic - in production, check for conflicts/issues)
            user_alert = None
            if context_data.contextLevel == "ticket":
                user_alert = f"AI agents are now aware of your {context_data.ticketID} context"

            # File tracking
            file_info = None
            if context_data.files:
                file_info = {
                    "count": len(context_data.files),
                    "files": context_data.files
                }

            # Log analytics event
            self._log_analytics_event(context_id, "context_stored", {
                "user_id": context_data.userId,
                "repo_id": context_data.repoID,
                "ticket_id": context_data.ticketID,
                "context_level": context_data.contextLevel
            })

            return ContextResponse(
                status="success",
                contextId=context_id,
                details=details,
                userAlert=user_alert,
                file=file_info,
                message="Workflow context successfully stored"
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

    # ============ CONTEXT DISCOVERY METHODS ============

    def search_contexts(
        self,
        repo_id: Optional[str] = None,
        ticket_id: Optional[str] = None,
        file_path: Optional[str] = None,
        context_level: Optional[str] = None,
        ai_client: Optional[str] = None,
        query_text: Optional[str] = None,
        limit: int = 10
    ) -> list[Dict[str, Any]]:
        """
        Search contexts with flexible filtering

        This is the core discovery method for AI agents to find relevant context
        """
        query = self.db.query(UserContext)

        # Filter by repoID
        if repo_id:
            query = query.filter(UserContext.context_data['repoID'].astext == repo_id)

        # Filter by ticketID
        if ticket_id:
            query = query.filter(UserContext.context_data['ticketID'].astext == ticket_id)

        # Filter by file path (partial match)
        if file_path:
            query = query.filter(
                UserContext.context_data['files'].astext.contains(file_path)
            )

        # Filter by context level
        if context_level:
            query = query.filter(
                UserContext.context_data['contextLevel'].astext == context_level
            )

        # Filter by AI client type
        if ai_client:
            query = query.filter(
                UserContext.context_data['AI_Client_type'].astext.contains(ai_client)
            )

        # Text search in details field
        if query_text:
            query = query.filter(
                UserContext.context_data['details'].astext.ilike(f'%{query_text}%')
            )

        # Order by most recent and limit results
        contexts = query.order_by(
            UserContext.timestamp.desc()
        ).limit(limit).all()

        return [ctx.to_dict() for ctx in contexts]

    def get_contexts_by_repo(self, repo_id: str, limit: int = 20) -> list[Dict[str, Any]]:
        """Get all contexts for a specific repository"""
        contexts = self.db.query(UserContext).filter(
            UserContext.context_data['repoID'].astext == repo_id
        ).order_by(UserContext.timestamp.desc()).limit(limit).all()

        return [ctx.to_dict() for ctx in contexts]

    def get_contexts_by_ticket(self, ticket_id: str, limit: int = 20) -> list[Dict[str, Any]]:
        """Get all contexts for a specific ticket"""
        contexts = self.db.query(UserContext).filter(
            UserContext.context_data['ticketID'].astext == ticket_id
        ).order_by(UserContext.timestamp.desc()).limit(limit).all()

        return [ctx.to_dict() for ctx in contexts]
