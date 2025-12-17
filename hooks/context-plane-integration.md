# Context Plane Integration

## Overview
This skill enables Claude to automatically check Context Plane for relevant organizational skills and knowledge when users describe tasks.

## When to Use
Automatically activate this skill when:
- User describes a new task or project
- User asks for help with something that might have organizational context
- User mentions testing, documentation, design, or other common engineering tasks

## How It Works

### 1. Automatic Skill Suggestions
When a user describes a task, query Context Plane for relevant skills:

```bash
curl -s -X POST "http://localhost:8000/api/v1/skills/suggest" \
  -H "Content-Type: application/json" \
  -d "{\"userPrompt\":\"USER_TASK_HERE\",\"context\":{}}"
```

### 2. Present Suggestions Naturally
Don't make a big deal about it. Simply say something like:

"I can help with that! I notice we have some relevant organizational skills that might be useful:
- **[Skill Name]** - [Brief description]

Would you like me to use this approach, or would you prefer a different method?"

### 3. Use the Skill
If the user accepts, follow the guidance from the skill's content (available via API).

## Commands Available

Users can also manually check for skills:
- `/check-skills` - Check for new/updated skills
- `/suggest-skill` - Get skill suggestions for a task
- `/browse-skills` - Browse all available skills

## API Endpoints

- `GET /api/v1/skills/updates` - Check for new skills and updates
- `POST /api/v1/skills/suggest` - Get skill suggestions (uses AWS Bedrock semantic search)
- `GET /api/skills` - Get all skills
- `GET /api/skills/{skill_id}` - Get specific skill details

## Example Flow

User: "I need to test my web application"

1. Query Context Plane: `{"userPrompt":"test my web application","context":{}}`
2. Get suggestion: "webapp-testing" skill (73% confidence)
3. Respond naturally: "I can help test your web application! I see we have a 'Web Application Testing' skill that uses Playwright. Would you like me to write some tests using that approach?"

## Implementation Notes

- Use semantic search - it understands intent, not just keywords
- Only suggest skills if confidence > 50%
- Don't overwhelm users - max 2-3 suggestions
- Make it conversational, not robotic
- Fall back to your general knowledge if no skills match
