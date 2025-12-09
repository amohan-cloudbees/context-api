# Context API Demo Guide

This guide shows you how to use the Context API with real examples.

## Quick Start

Your API is running at: **http://localhost:8000**

## Available Endpoints

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Context API",
  "version": "1.0.0"
}
```

---

## 2. Store Context Data

### Example 1: Simple User Conversation
```bash
curl -X POST http://localhost:8000/api/context \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user_alice",
    "sessionId": "session_001",
    "appContext": {
      "appName": "ChatApp",
      "version": "2.0.1",
      "platform": "web"
    },
    "conversationHistory": [
      {
        "role": "user",
        "message": "What are your business hours?",
        "timestamp": "2024-12-09T10:00:00Z"
      },
      {
        "role": "assistant",
        "message": "We are open Monday-Friday, 9 AM to 5 PM",
        "timestamp": "2024-12-09T10:00:15Z"
      }
    ],
    "userPreferences": {
      "theme": "dark",
      "language": "en",
      "notifications": true
    },
    "deviceInfo": {
      "platform": "web",
      "browser": "Chrome",
      "version": "120.0"
    },
    "activityLog": [
      {
        "action": "page_view",
        "page": "/support",
        "timestamp": "2024-12-09T09:58:00Z"
      }
    ],
    "location": {
      "country": "US",
      "city": "New York",
      "timezone": "EST"
    },
    "timestamp": "2024-12-09T10:00:00Z"
  }'
```

**Response:**
```json
{
  "status": "success",
  "contextId": "ctx_abc123def456",
  "enrichedContext": {
    "summary": "User user_alice interaction in session session_001",
    "keyTopics": ["conversation", "interaction"],
    "userIntent": "conversation_started",
    "sentimentAnalysis": {
      "sentiment": "neutral",
      "confidence": 0.75
    }
  },
  "recommendations": [
    "Greet the user warmly",
    "Ask how you can help",
    "Respond in en language"
  ],
  "message": "Context successfully stored and enriched"
}
```

---

### Example 2: E-commerce Shopping Session
```bash
curl -X POST http://localhost:8000/api/context \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user_bob",
    "sessionId": "session_002",
    "appContext": {
      "appName": "ShopApp",
      "page": "product_details",
      "productId": "PROD_12345"
    },
    "conversationHistory": [
      {
        "role": "user",
        "message": "Do you have this in size medium?",
        "timestamp": "2024-12-09T11:00:00Z"
      }
    ],
    "userPreferences": {
      "size": "M",
      "color": "blue",
      "priceRange": "50-100"
    },
    "deviceInfo": {
      "platform": "mobile",
      "os": "iOS",
      "version": "17.1"
    },
    "activityLog": [
      {
        "action": "product_view",
        "productId": "PROD_12345",
        "timestamp": "2024-12-09T10:55:00Z"
      },
      {
        "action": "add_to_cart",
        "productId": "PROD_12345",
        "timestamp": "2024-12-09T11:02:00Z"
      }
    ],
    "location": {
      "country": "US",
      "city": "Los Angeles"
    },
    "timestamp": "2024-12-09T11:00:00Z"
  }'
```

---

### Example 3: Customer Support Interaction
```bash
curl -X POST http://localhost:8000/api/context \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user_charlie",
    "sessionId": "session_003",
    "appContext": {
      "appName": "SupportPortal",
      "ticketId": "TICKET_789",
      "department": "technical_support"
    },
    "conversationHistory": [
      {
        "role": "user",
        "message": "My app keeps crashing when I try to upload photos",
        "timestamp": "2024-12-09T12:00:00Z"
      },
      {
        "role": "assistant",
        "message": "I understand the issue. Let me help you troubleshoot.",
        "timestamp": "2024-12-09T12:00:30Z"
      },
      {
        "role": "user",
        "message": "It happens every time on iOS",
        "timestamp": "2024-12-09T12:01:00Z"
      }
    ],
    "userPreferences": {
      "contactMethod": "email",
      "language": "en"
    },
    "deviceInfo": {
      "platform": "iOS",
      "appVersion": "3.2.1",
      "osVersion": "17.2"
    },
    "activityLog": [
      {
        "action": "error_occurred",
        "errorCode": "UPLOAD_FAILED",
        "timestamp": "2024-12-09T11:55:00Z"
      }
    ],
    "location": {
      "country": "US",
      "city": "Chicago"
    },
    "timestamp": "2024-12-09T12:00:00Z"
  }'
```

---

## 3. Retrieve Stored Context

### Get Context by ID
```bash
curl http://localhost:8000/api/context/ctx_abc123def456
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid-here",
    "context_id": "ctx_abc123def456",
    "user_id": "user_alice",
    "session_id": "session_001",
    "app_context": { "appName": "ChatApp" },
    "conversation_history": [...],
    "user_preferences": {...},
    "device_info": {...},
    "activity_log": [...],
    "location": {...},
    "timestamp": "2024-12-09T10:00:00",
    "created_at": "2024-12-09T10:00:05",
    "updated_at": "2024-12-09T10:00:05"
  }
}
```

---

### Get All Contexts for a User
```bash
# Get last 10 contexts for user_alice
curl http://localhost:8000/api/contexts/user/user_alice?limit=10
```

**Response:**
```json
{
  "status": "success",
  "count": 5,
  "data": [
    {
      "context_id": "ctx_latest",
      "session_id": "session_005",
      "timestamp": "2024-12-09T15:00:00",
      ...
    },
    {
      "context_id": "ctx_older",
      "session_id": "session_004",
      "timestamp": "2024-12-09T14:00:00",
      ...
    }
  ]
}
```

---

## 4. Python Examples

### Basic Usage
```python
import requests
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000/api"

# Store context
def store_context(user_id, session_id, message):
    response = requests.post(
        f"{BASE_URL}/context",
        json={
            "userId": user_id,
            "sessionId": session_id,
            "appContext": {"appName": "MyApp"},
            "conversationHistory": [
                {
                    "role": "user",
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            ],
            "userPreferences": {},
            "deviceInfo": {},
            "activityLog": [],
            "location": {},
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )
    return response.json()

# Example usage
result = store_context("user123", "session456", "Hello, I need help")
print(f"Context ID: {result['contextId']}")
print(f"Recommendations: {result['recommendations']}")
```

### Get User Context History
```python
def get_user_contexts(user_id, limit=10):
    response = requests.get(
        f"{BASE_URL}/contexts/user/{user_id}",
        params={"limit": limit}
    )
    return response.json()

# Example usage
contexts = get_user_contexts("user123", limit=5)
print(f"Found {contexts['count']} contexts")
for ctx in contexts['data']:
    print(f"- {ctx['context_id']} at {ctx['timestamp']}")
```

### Full Application Example
```python
import requests
from datetime import datetime

class ContextAPIClient:
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url

    def store_context(self, user_id, session_id, conversation,
                     app_context=None, preferences=None):
        payload = {
            "userId": user_id,
            "sessionId": session_id,
            "appContext": app_context or {},
            "conversationHistory": conversation,
            "userPreferences": preferences or {},
            "deviceInfo": {},
            "activityLog": [],
            "location": {},
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        response = requests.post(
            f"{self.base_url}/context",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_context(self, context_id):
        response = requests.get(
            f"{self.base_url}/context/{context_id}"
        )
        response.raise_for_status()
        return response.json()

    def get_user_contexts(self, user_id, limit=10):
        response = requests.get(
            f"{self.base_url}/contexts/user/{user_id}",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()

# Usage
client = ContextAPIClient()

# Store context
result = client.store_context(
    user_id="alice",
    session_id="sess_001",
    conversation=[
        {
            "role": "user",
            "message": "What's your return policy?",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    ],
    app_context={"appName": "RetailApp", "page": "product"},
    preferences={"language": "en", "theme": "dark"}
)

print(f"Stored context: {result['contextId']}")
print(f"AI Summary: {result['enrichedContext']['summary']}")
print(f"Recommendations: {result['recommendations']}")

# Retrieve user's contexts
user_contexts = client.get_user_contexts("alice", limit=5)
print(f"\nUser has {user_contexts['count']} contexts")
```

---

## 5. JavaScript/Node.js Examples

### Using Fetch (Browser)
```javascript
// Store context
async function storeContext(userId, sessionId, message) {
  const response = await fetch('http://localhost:8000/api/context', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      userId: userId,
      sessionId: sessionId,
      appContext: { appName: 'WebApp' },
      conversationHistory: [
        {
          role: 'user',
          message: message,
          timestamp: new Date().toISOString()
        }
      ],
      userPreferences: {},
      deviceInfo: {},
      activityLog: [],
      location: {},
      timestamp: new Date().toISOString()
    })
  });

  return await response.json();
}

// Usage
storeContext('user123', 'session456', 'Hello!')
  .then(result => {
    console.log('Context ID:', result.contextId);
    console.log('Recommendations:', result.recommendations);
  });
```

### Using Axios (Node.js)
```javascript
const axios = require('axios');

const API_BASE = 'http://localhost:8000/api';

// Store context
async function storeContext(data) {
  try {
    const response = await axios.post(`${API_BASE}/context`, {
      userId: data.userId,
      sessionId: data.sessionId,
      appContext: data.appContext || {},
      conversationHistory: data.conversation || [],
      userPreferences: data.preferences || {},
      deviceInfo: {},
      activityLog: [],
      location: {},
      timestamp: new Date().toISOString()
    });

    return response.data;
  } catch (error) {
    console.error('Error storing context:', error.response.data);
    throw error;
  }
}

// Get user contexts
async function getUserContexts(userId, limit = 10) {
  try {
    const response = await axios.get(
      `${API_BASE}/contexts/user/${userId}`,
      { params: { limit } }
    );
    return response.data;
  } catch (error) {
    console.error('Error getting contexts:', error.response.data);
    throw error;
  }
}

// Usage
(async () => {
  // Store context
  const result = await storeContext({
    userId: 'user123',
    sessionId: 'session456',
    conversation: [
      {
        role: 'user',
        message: 'I need help with my order',
        timestamp: new Date().toISOString()
      }
    ],
    appContext: { appName: 'ShopApp', page: 'orders' },
    preferences: { language: 'en' }
  });

  console.log('Stored:', result.contextId);

  // Get user's contexts
  const contexts = await getUserContexts('user123', 5);
  console.log(`Found ${contexts.count} contexts`);
})();
```

---

## 6. Testing with Postman

### Setup
1. Open Postman
2. Create new request
3. Set method to POST
4. URL: `http://localhost:8000/api/context`
5. Headers: `Content-Type: application/json`
6. Body (raw JSON):

```json
{
  "userId": "test_user",
  "sessionId": "test_session",
  "appContext": {
    "appName": "TestApp",
    "version": "1.0.0"
  },
  "conversationHistory": [
    {
      "role": "user",
      "message": "Test message",
      "timestamp": "2024-12-09T10:00:00Z"
    }
  ],
  "userPreferences": {
    "theme": "dark"
  },
  "deviceInfo": {
    "platform": "web"
  },
  "activityLog": [],
  "location": {
    "country": "US"
  },
  "timestamp": "2024-12-09T10:00:00Z"
}
```

---

## 7. Interactive API Documentation

Open in your browser: **http://localhost:8000/docs**

This provides an interactive interface where you can:
- See all available endpoints
- Test endpoints directly in the browser
- View request/response schemas
- See example requests and responses

---

## 8. Common Use Cases

### Chat Application
Store each conversation turn with context about the user's state, preferences, and conversation history.

### E-commerce
Track user browsing behavior, cart actions, and preferences to provide personalized recommendations.

### Customer Support
Maintain full context of support interactions including previous issues, resolutions, and user preferences.

### Analytics
Track user journey across your application with detailed activity logs and session information.

### Personalization
Use stored preferences and history to customize user experience across sessions and devices.

---

## Troubleshooting

### Check if API is running
```bash
curl http://localhost:8000/api/health
```

### View API logs
Check the terminal where you ran `python main.py`

### Restart API
```bash
cd ~/Desktop/context-api
source venv/bin/activate
python main.py
```

### Check database
```bash
psql -d context_db -c "SELECT COUNT(*) FROM user_contexts;"
```

---

## Next Steps

1. Integrate the API into your application
2. Customize the AI enrichment logic in `api/services/context_service.py`
3. Add authentication/authorization
4. Deploy to production
5. Add monitoring and analytics

For more information, see the README.md file.
