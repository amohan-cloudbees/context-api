"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from config.database import check_db_connection, init_db
from api.routes import context_api, skill_routes
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## Context Plane API for Unify AI

    This API provides the foundation for the Context Plane - a knowledge base system
    that manages workflow context for AI agents, code repositories, and ticket workflows.

    ### Features:
    - Store workflow context (repos, tickets, files)
    - Multi-level context (global, project, ticket)
    - AI agent coordination (Claude, AWS Q, OpenCase)
    - Analytics tracking
    - Context retrieval and discovery

    ### Endpoints:
    - `POST /api/context` - Store workflow context
    - `GET /api/context/{context_id}` - Retrieve specific context
    - `GET /api/contexts/user/{user_id}` - Get user's contexts
    - `GET /api/health` - Health check
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(context_api.router)
app.include_router(skill_routes.router)


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Check database connection
    if check_db_connection():
        logger.info("Database connection established")
    else:
        logger.error("Failed to connect to database")

    # Initialize database tables (in production, use migrations)
    if settings.DEBUG:
        try:
            init_db()
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info(f"Shutting down {settings.APP_NAME}")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
