# Context API - Unify AI

A FastAPI service for managing workflow context data for AI agents, code repositories, and ticket workflows. This API serves as the foundation for the Context Plane - a knowledge base that enables AI agents to access relevant contextual information.

## Features

- **Workflow Context Storage**: Store context for repos, tickets, and AI agent coordination
- **Multi-Level Context**: Support for global, project, and ticket-level context
- **Context Discovery & Search**: Flexible search API for AI agents to find relevant context
  - Search by repository, ticket, file path
  - Filter by context level and AI client type
  - Full-text search in details field
  - Optimized with PostgreSQL JSONB indexes
- **Context Retrieval**: Query contexts by ID, user, or workflow
- **Analytics Tracking**: Monitor context usage and patterns
- **AI Agent Integration**: Enable Claude, AWS Q, and other AI tools to access context
- **Auto-generated API Documentation**: Interactive Swagger/ReDoc documentation

## Tech Stack

- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Validation**: Pydantic v2
- **Server**: Uvicorn (ASGI)

## Project Structure

```
context-api/
├── api/
│   ├── routes/          # API endpoints
│   ├── models/          # Database models
│   ├── schemas/         # Request/response schemas
│   └── services/        # Business logic
├── config/              # Configuration
├── database/            # Database migrations
├── analytics/           # Analytics tracking
├── tests/               # Unit tests
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── .env.example         # Environment variables template
```

## Quick Start

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

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

# Option 2: Run SQL migration manually
psql -U postgres -d context_db -f database/migrations/001_create_context_tables.sql
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

## API Endpoints

### Store Context
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
- `HOST` and `PORT`: Server binding
- `DEBUG`: Enable debug mode
- `ALLOWED_ORIGINS`: CORS allowed origins
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Production Deployment

For production deployment:

1. Set `DEBUG=false` in `.env`
2. Use proper database credentials
3. Set up proper logging and monitoring
4. Add authentication/authorization
5. Use environment-specific `.env` files

## Future Enhancements

- Integrate real AI/ML models for enrichment
- Add authentication (JWT, OAuth2)
- Implement caching (Redis)
- Add rate limiting
- WebSocket support for real-time updates
- Docker containerization

## Support

For issues or questions, please open an issue in the repository.
