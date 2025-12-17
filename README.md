# Context Plane - CloudBees AI Knowledge Management

A FastAPI service that enables AI agents like Claude Code to discover and execute organizational knowledge through intelligent skill discovery. Context Plane transforms static documentation into executable AI skills, ensuring every developer has access to best practices, tools, and workflows through natural language interaction.

## Features

### Skills System (Primary Feature)
- **AI Skills Catalog**: Centralized repository of AI agent profiles (skills) with semantic versioning
- **Semantic Skill Discovery**: Natural language skill suggestions powered by AWS Bedrock Titan Embeddings
- **Executable Skills**: Skills contain instructions, scripts, and resources for Claude to execute
- **Version Management**: Track skill updates and notify users of new capabilities
- **Skill Ingestion**: Automatically ingest skills from directories with embedding generation

### Claude Code Integration
- **Session Hooks**: Automatic skill update notifications on session start/end
- **Natural Language Interface**: Users describe tasks; Claude automatically queries Context Plane
- **Slash Commands**: `/check-skills`, `/suggest-skill`, `/browse-skills` for manual discovery
- **Context Plane Integration Skill**: Teaches Claude to automatically query for relevant skills

### Workflow Context Storage (Secondary Feature)
- **Multi-Level Context**: Support for global, project, and ticket-level context
- **Context Discovery & Search**: Flexible search API for AI agents to find relevant context
- **Analytics Tracking**: Monitor context usage and patterns
- **Auto-generated API Documentation**: Interactive Swagger/ReDoc documentation

## Tech Stack

- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL 14+ with SQLAlchemy ORM
- **AI/ML**: AWS Bedrock Titan Embeddings (1024-dimensional vectors)
- **Validation**: Pydantic v2
- **Server**: Uvicorn (ASGI)
- **Integration**: Claude Code (REST API + Session Hooks)

## Project Structure

```
context-api/
├── api/
│   ├── routes/          # API endpoints
│   │   ├── context_api.py      # Context CRUD operations
│   │   ├── skill_routes.py     # Skills management API
│   │   └── prehook_routes.py   # Claude Code integration endpoints
│   ├── models/          # Database models
│   │   ├── context.py          # UserContext, ContextAnalytics
│   │   ├── skill.py            # Skill model with embeddings
│   │   └── user_skill.py       # User skill tracking
│   ├── schemas/         # Pydantic validation schemas
│   └── services/        # Business logic
│       ├── context_service.py     # Context management
│       ├── skill_service.py       # Skills ingestion & search
│       ├── prehook_service.py     # Claude Code integration
│       └── embedding_service.py   # AWS Bedrock integration
├── config/              # Configuration
│   ├── database.py      # Database connection & session management
│   └── settings.py      # Application configuration
├── database/            # Database migrations
│   └── migrations/      # SQL migration files (001-010)
├── hooks/               # Claude Code integration scripts
│   ├── README.md
│   ├── context_plane_session_start.sh
│   ├── context_plane_session_end.sh
│   ├── setup_local_demo.sh
│   └── demo_workflow.sh
├── skills/              # 13 skill directories with bundled resources
│   ├── doc-coauthoring/
│   ├── docx/
│   ├── frontend-design/
│   ├── internal-comms/
│   ├── mcp-builder/
│   ├── pdf/
│   ├── pptx/
│   ├── skill-creator/
│   ├── web-artifacts-builder/
│   ├── webapp-testing/
│   ├── xlsx/
│   └── lucky-number-context-plane-team/
├── scripts/
│   └── generate_skill_embeddings.py  # Bedrock embedding generation
├── analytics/           # Analytics tracking
├── tests/               # Unit tests
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── PROJECT_SUMMARY.md   # Detailed project documentation
```

## Quick Start

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 14 or higher
- pip (Python package manager)
- AWS Account with Bedrock access (for semantic search)
- Claude Code CLI (for integration features)

### Setup

```bash
# Navigate to project directory
cd ~/Desktop/context-api

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Configure Database

```bash
# Create PostgreSQL database
createdb context_db

# Or using psql
psql -U postgres
CREATE DATABASE context_db;
\q

# Copy environment template
cp .env.example .env

# Edit .env and update DATABASE_URL
# DATABASE_URL=postgresql://your_user:your_password@localhost:5432/context_db
```

### Run Database Migrations

```bash
# Option 1: Let FastAPI create tables automatically (development only)
# Tables will be created on first run when DEBUG=true

# Option 2: Run SQL migrations manually (recommended for production)
psql -U postgres -d context_db -f database/migrations/001_create_context_tables.sql
psql -U postgres -d context_db -f database/migrations/005_add_skills_table.sql
psql -U postgres -d context_db -f database/migrations/006_add_user_skills_table.sql
# ... run remaining migrations as needed
```

### Configure AWS Bedrock (for Semantic Search)

```bash
# Set AWS credentials in .env file
echo "AWS_REGION=us-east-1" >> .env
echo "AWS_ACCESS_KEY_ID=your_access_key" >> .env
echo "AWS_SECRET_ACCESS_KEY=your_secret_key" >> .env

# Or use AWS CLI configuration
aws configure
```

### Start the Server

```bash
# Development mode (with auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Ingest Skills into Database

```bash
# Ingest skills from the skills directory
curl -X POST http://localhost:8000/api/skills/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory_path":"./skills"}'

# Generate embeddings for semantic search
python scripts/generate_skill_embeddings.py

# Verify skills were ingested
curl http://localhost:8000/api/skills | jq '.data[] | {name: .title, version: .version}'
```

### Setup Claude Code Integration

**Required for full Context Plane functionality.** These commands provide the user interface for skill discovery and management.

#### Automated Setup (Recommended)

```bash
cd hooks
./setup_local_demo.sh
```

This script automatically:
- Installs session hooks (`session_start.sh`, `session_end.sh`)
- Installs slash commands (`/browse-skills`, `/check-skills`, `/suggest-skill`)
- Creates skills directory and manifest
- Sets up Claude Code configuration

#### Manual Setup

If you prefer manual installation:

```bash
# 1. Copy session hooks to Claude Code hooks directory
mkdir -p ~/.claude/hooks
cp hooks/context_plane_session_start.sh ~/.claude/hooks/
cp hooks/context_plane_session_end.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/context_plane_session_start.sh
chmod +x ~/.claude/hooks/context_plane_session_end.sh

# 2. Copy slash commands (REQUIRED for Context Plane UI)
mkdir -p ~/.claude/commands
cp hooks/commands/*.md ~/.claude/commands/

# 3. Copy the Context Plane integration skill
mkdir -p ~/.claude/skills
cp hooks/context-plane-integration.md ~/.claude/skills/

# 4. Configure Claude Code settings
# Add to ~/.claude/settings.json:
{
  "hooks": {
    "session_start": "~/.claude/hooks/context_plane_session_start.sh",
    "session_end": "~/.claude/hooks/context_plane_session_end.sh"
  }
}

# 5. Set Context Plane API endpoint (optional, defaults to localhost:8000)
export CONTEXT_PLANE_API_ENDPOINT="http://localhost:8000"
```

#### Available Slash Commands

After setup, restart Claude Code and use these commands:

- **`/browse-skills`** - Browse new skills you don't have installed
  - Shows only skills you haven't installed yet
  - Displays in formatted boxes following Pre-Hook specification
  - Shows updates available for installed skills

- **`/check-skills`** - Check for new skills and updates since last session
  - Tracks your last check timestamp
  - Shows new skills published since your last check
  - Shows version updates for installed skills

- **`/suggest-skill`** - Get AI-powered skill recommendations
  - Describe your task in natural language
  - Uses AWS Bedrock Titan semantic search
  - Returns confidence scores and reasoning

#### Verification

After setup, verify installation:

```bash
# Check hooks are installed
ls -la ~/.claude/hooks/

# Check commands are installed
ls -la ~/.claude/commands/

# Check skills directory exists
ls -la ~/.claude/skills/

# Test API connectivity
curl http://localhost:8000/api/health
```

Now when you start Claude Code, it will automatically check for new skills and you can use:
- **Slash commands**: `/browse-skills`, `/check-skills`, `/suggest-skill`
- **Natural language**: "I need to test my web application" (Claude automatically queries Context Plane)

## API Endpoints

### Skills API

#### List All Skills
```http
GET /api/skills
```

Returns all available skills with their metadata.

**Response:**
```json
{
  "status": "success",
  "count": 13,
  "data": [
    {
      "id": "uuid",
      "skill_id": "webapp-testing",
      "title": "Web Application Testing",
      "description": "Write native Python Playwright scripts for web testing",
      "category": "testing",
      "version": "1.0.0",
      "tags": ["playwright", "testing", "e2e"]
    }
  ]
}
```

#### Get Skill Suggestions (Semantic Search)
```http
POST /api/v1/skills/suggest
```

**Request Body:**
```json
{
  "userPrompt": "help me test my web application",
  "context": {}
}
```

**Response:**
```json
{
  "suggestions": [
    {
      "skillId": "webapp-testing",
      "confidence": 0.73,
      "reasoning": "Semantic similarity score using Bedrock Titan embeddings",
      "skillMetadata": {
        "name": "Web Application Testing",
        "description": "Write native Python Playwright scripts",
        "category": "testing",
        "capabilities": ["playwright", "testing", "e2e"]
      }
    }
  ]
}
```

#### Check for Skill Updates
```http
GET /api/v1/skills/updates?user_id=demo_user&installed_skills=[...]&last_check=2025-01-01T00:00:00Z
```

Returns available updates for installed skills and new skills since last check.

**Response:**
```json
{
  "availableUpdates": [
    {
      "skillId": "webapp-testing",
      "name": "Web Application Testing",
      "currentVersion": "0.9.0",
      "latestVersion": "1.0.0",
      "category": "testing"
    }
  ],
  "newSkills": [
    {
      "skillId": "mcp-builder",
      "name": "MCP Server Development Guide",
      "latestVersion": "1.0.0",
      "category": "documentation"
    }
  ]
}
```

#### Get Specific Skill
```http
GET /api/skills/{skill_id}
```

Returns complete skill details including markdown content.

#### Ingest Skills
```http
POST /api/skills/ingest
```

**Request Body:**
```json
{
  "directory_path": "./skills"
}
```

Ingests all skills from the specified directory and generates embeddings.

### Context API

#### Store Context
```http
POST /api/context
```

Store Unify AI workflow context for code repositories and tickets.

**Request Body:**
```json
{
  "userId": "developer123",
  "sessionId": "work_session_456",
  "repoID": "repo_abc123",
  "catalogID": "unify_map",
  "ticketID": "JIRA-1234",
  "contextLevel": "ticket",
  "AI_Client_type": ["Claude", "AWSQ"],
  "details": "I am trying to fix the authentication bug in the login module",
  "files": [
    {
      "path": "src/auth/login.py",
      "type": "python",
      "action": "modified"
    }
  ],
  "conversationHistory": [
    {
      "role": "user",
      "aiClient": "Claude",
      "message": "Can you help me debug the authentication issue?",
      "timestamp": "2024-12-09T09:55:00Z"
    },
    {
      "role": "assistant",
      "aiClient": "Claude",
      "message": "I'll help you investigate the login.py file.",
      "timestamp": "2024-12-09T09:56:00Z"
    }
  ],
  "status": "in_progress",
  "blockedBy": null,
  "timestamp": "2024-12-09T10:00:00Z"
}
```

**New Fields (Optional):**
- `conversationHistory`: Array of dialogue between user and AI agents - enables AI handoff and context preservation
- `status`: Workflow status (`not_started`, `in_progress`, `blocked`, `needs_review`, `completed`)
- `blockedBy`: Ticket ID or reason if status is "blocked"

**Response:**
```json
{
  "status": "success",
  "contextId": "ctx_xyz789",
  "details": "Context captured for ticket JIRA-1234 in repo repo_abc123",
  "userAlert": "AI agents are now aware of your JIRA-1234 context",
  "file": {
    "count": 1,
    "files": [
      {
        "path": "src/auth/login.py",
        "type": "python",
        "action": "modified"
      }
    ]
  },
  "message": "Workflow context successfully stored"
}
```

### Retrieve Context
```http
GET /api/context/{context_id}
```

### Get User Contexts
```http
GET /api/contexts/user/{user_id}?limit=10
```

### Search Contexts (Context Discovery)
```http
GET /api/contexts/search?repoID=repo_abc123&query=authentication&limit=10
```

Search and discover contexts with flexible filtering. This is the primary endpoint for AI agents to find relevant context.

**Query Parameters:**
- `repoID`: Filter by repository ID
- `ticketID`: Filter by ticket ID
- `filePath`: Search by file path (partial match supported)
- `contextLevel`: Filter by level (global, project, ticket)
- `aiClient`: Filter by AI client type (Claude, AWSQ, etc.)
- `status`: Filter by workflow status (not_started, in_progress, blocked, needs_review, completed)
- `query`: Text search in details field
- `limit`: Maximum results (1-100, default 10)

**Example Response:**
```json
{
  "status": "success",
  "count": 3,
  "filters": {
    "repoID": "repo_abc123",
    "query": "authentication"
  },
  "data": [...]
}
```

### Get Repository Contexts
```http
GET /api/contexts/repo/{repo_id}?limit=20
```

Get all contexts for a specific repository.

### Get Ticket Contexts
```http
GET /api/contexts/ticket/{ticket_id}?limit=20
```

Get all contexts for a specific ticket (e.g., JIRA-1234).

### Health Check
```http
GET /api/health
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=api tests/
```

## Example Usage with cURL

```bash
# Store context
curl -X POST http://localhost:8000/api/context \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "developer123",
    "sessionId": "work_session_456",
    "repoID": "repo_abc123",
    "catalogID": "unify_map",
    "ticketID": "JIRA-1234",
    "contextLevel": "ticket",
    "AI_Client_type": ["Claude", "AWSQ"],
    "details": "I am trying to fix the authentication bug in the login module",
    "files": [{"path": "src/auth/login.py", "type": "python", "action": "modified"}],
    "timestamp": "2024-12-09T10:00:00Z"
  }'

# Retrieve specific context
curl http://localhost:8000/api/context/ctx_xyz789

# Get all contexts for a user
curl http://localhost:8000/api/contexts/user/developer123?limit=10

# Search contexts by repository
curl "http://localhost:8000/api/contexts/search?repoID=repo_abc123&limit=5"

# Search contexts with text query
curl "http://localhost:8000/api/contexts/search?query=authentication&contextLevel=ticket"

# Search by file path
curl "http://localhost:8000/api/contexts/search?filePath=src/auth/login.py"

# Search by workflow status
curl "http://localhost:8000/api/contexts/search?status=blocked"
curl "http://localhost:8000/api/contexts/search?status=in_progress&repoID=repo_abc123"

# Get all contexts for a repository
curl http://localhost:8000/api/contexts/repo/repo_abc123

# Get all contexts for a ticket
curl http://localhost:8000/api/contexts/ticket/JIRA-1234
```

## Example Usage with Python

```python
import requests
from datetime import datetime

# Store workflow context
response = requests.post(
    "http://localhost:8000/api/context",
    json={
        "userId": "developer123",
        "sessionId": "work_session_456",
        "repoID": "repo_abc123",
        "catalogID": "unify_map",
        "ticketID": "JIRA-1234",
        "contextLevel": "ticket",
        "AI_Client_type": ["Claude", "AWSQ"],
        "details": "I am trying to fix the authentication bug in the login module",
        "files": [
            {
                "path": "src/auth/login.py",
                "type": "python",
                "action": "modified"
            }
        ],
        "timestamp": datetime.utcnow().isoformat()
    }
)

result = response.json()
context_id = result["contextId"]
print(f"Stored context: {context_id}")
print(f"Details: {result['details']}")
print(f"User Alert: {result.get('userAlert')}")

# Retrieve the stored context
context = requests.get(f"http://localhost:8000/api/context/{context_id}")
print(f"Retrieved context: {context.json()}")

# Search for contexts related to authentication in a repo
search_results = requests.get(
    "http://localhost:8000/api/contexts/search",
    params={
        "repoID": "repo_abc123",
        "query": "authentication",
        "limit": 5
    }
)
print(f"Found {search_results.json()['count']} matching contexts")

# Get all contexts for a specific ticket
ticket_contexts = requests.get(
    "http://localhost:8000/api/contexts/ticket/JIRA-1234"
)
print(f"Ticket has {ticket_contexts.json()['count']} contexts")
```

## Configuration

Edit `.env` file to configure:

- `DATABASE_URL`: PostgreSQL connection string
- `HOST` and `PORT`: Server binding (default: 0.0.0.0:8000)
- `DEBUG`: Enable debug mode (default: true for development)
- `ALLOWED_ORIGINS`: CORS allowed origins
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `AWS_REGION`: AWS region for Bedrock (default: us-east-1)
- `AWS_ACCESS_KEY_ID`: AWS access key (optional if using AWS CLI config)
- `AWS_SECRET_ACCESS_KEY`: AWS secret key (optional if using AWS CLI config)

## Production Deployment

For production deployment:

1. Set `DEBUG=false` in `.env`
2. Use proper database credentials
3. Set up proper logging and monitoring
4. Add authentication/authorization
5. Use environment-specific `.env` files

## Current Features

✅ **Skills System** - AI agent profiles with semantic versioning
✅ **Semantic Search** - AWS Bedrock Titan embeddings with cosine similarity
✅ **Claude Code Integration** - Session hooks and natural language interface
✅ **Version Management** - Track and notify skill updates
✅ **Skill Ingestion** - Automatic ingestion from directories
✅ **PostgreSQL Storage** - JSONB storage with embeddings
✅ **REST API** - Complete CRUD operations
✅ **Interactive Documentation** - Swagger UI and ReDoc

## Roadmap

### Phase 1 (Completed)
- ✅ Skills catalog and management
- ✅ Semantic skill discovery
- ✅ Claude Code session hooks
- ✅ Update notifications

### Phase 2 (In Progress)
- 🔄 Documentation context (runbooks, design docs, coding standards)
- 🔄 Team collaboration features (skill sharing, ratings, reviews)
- 🔄 Authentication (JWT, OAuth2)
- 🔄 Enhanced analytics and usage metrics

### Phase 3 (Planned)
- SDLC state context (real-time project status, dependencies, blockers)
- Slack AIFR integration
- IDE plugins (VSCode, IntelliJ)
- Caching layer (Redis)
- Rate limiting
- WebSocket support for real-time updates
- Docker containerization
- Kubernetes deployment

## Architecture

Context Plane follows a three-tier context architecture:

1. **Skills (Context Type 1)** - AI agent profiles with executable instructions ✅ **IMPLEMENTED**
2. **Documentation Context (Type 2)** - Organizational documentation and standards 🔄 **PLANNED**
3. **SDLC State Context (Type 3)** - Real-time development state 🔄 **PLANNED**

## Contributing

Please read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for detailed project documentation.

## Support

For issues or questions, please open an issue in the repository.

## License

Copyright © 2025 CloudBees, Inc.
