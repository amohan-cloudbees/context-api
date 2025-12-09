# Context API - Unify AI

A FastAPI service for storing and enriching user context data with AI-powered insights and recommendations.

## Features

- **Context Storage**: Store user interaction context data
- **AI Enrichment**: Automatically analyze and enrich context with AI
- **Smart Recommendations**: Generate intelligent recommendations
- **Analytics**: Track API usage and context metrics
- **Context Retrieval**: Query contexts by ID or user
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

**Request Body:**
```json
{
  "userId": "user123",
  "sessionId": "session456",
  "appContext": {
    "appName": "MyApp",
    "version": "1.0.0"
  },
  "conversationHistory": [
    {
      "role": "user",
      "message": "Hello",
      "timestamp": "2024-12-09T10:00:00Z"
    }
  ],
  "userPreferences": {
    "theme": "dark",
    "language": "en"
  },
  "deviceInfo": {
    "platform": "iOS",
    "deviceId": "device789"
  },
  "activityLog": [],
  "location": {
    "country": "US",
    "city": "San Francisco"
  },
  "timestamp": "2024-12-09T10:00:00Z"
}
```

**Response:**
```json
{
  "status": "success",
  "contextId": "ctx_abc123",
  "enrichedContext": {
    "summary": "User initiated conversation",
    "keyTopics": ["conversation", "interaction"],
    "userIntent": "conversation_started",
    "sentimentAnalysis": {
      "sentiment": "neutral",
      "confidence": 0.75
    }
  },
  "recommendations": [
    "Greet the user warmly",
    "Ask how you can help"
  ],
  "message": "Context successfully stored and enriched"
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
    "userId": "user123",
    "sessionId": "session456",
    "appContext": {"appName": "TestApp"},
    "conversationHistory": [],
    "userPreferences": {},
    "deviceInfo": {},
    "activityLog": [],
    "location": {},
    "timestamp": "2024-12-09T10:00:00Z"
  }'

# Retrieve context
curl http://localhost:8000/api/context/ctx_abc123

# Get user contexts
curl http://localhost:8000/api/contexts/user/user123?limit=5
```

## Example Usage with Python

```python
import requests
from datetime import datetime

# Store context
response = requests.post(
    "http://localhost:8000/api/context",
    json={
        "userId": "user123",
        "sessionId": "session456",
        "appContext": {"appName": "MyApp"},
        "conversationHistory": [
            {
                "role": "user",
                "message": "Hello",
                "timestamp": datetime.utcnow().isoformat()
            }
        ],
        "userPreferences": {"theme": "dark"},
        "deviceInfo": {"platform": "web"},
        "activityLog": [],
        "location": {"country": "US"},
        "timestamp": datetime.utcnow().isoformat()
    }
)

result = response.json()
context_id = result["contextId"]
print(f"Stored context: {context_id}")
print(f"Recommendations: {result['recommendations']}")
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
