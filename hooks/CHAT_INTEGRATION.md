# Context Plane - Chat-Visible Integration

## Overview

The background hooks work but run silently. This new integration makes Context Plane visible in your Claude Code chat through slash commands and automatic skill suggestions.

## What Was Created

### 1. Slash Commands (Visible in Chat)

Three new commands you can run anytime:

#### `/check-skills`
Check for new and updated skills from your organization.

```bash
/check-skills
```

Shows:
- New skills available
- Updates for installed skills
- Detailed info about each skill

#### `/suggest-skill`
Get skill suggestions based on your task (uses AI semantic search).

```bash
/suggest-skill
```

You'll be asked what you want to do, then Context Plane will suggest relevant skills with confidence scores.

#### `/browse-skills`
Browse all available skills in the organization.

```bash
/browse-skills
```

Shows all skills organized by category.

### 2. Automatic Integration Skill

Location: `~/.claude/skills/context-plane-integration.md`

This skill enables Claude to automatically:
- Check Context Plane when you describe tasks
- Suggest relevant organizational skills naturally in conversation
- Use semantic search to understand your intent

**How it works:**
When you say something like "I need to test my web application", Claude will:
1. Query Context Plane's semantic search API
2. Find relevant skills (e.g., "webapp-testing" with 73% confidence)
3. Suggest it conversationally: "I see we have a Web Application Testing skill that uses Playwright. Would you like me to use that approach?"

## How to Use

### Manual Checks (New Sessions)

When you start a new Claude Code session, run:

```bash
/check-skills
```

This shows you what's new since your last session.

### Task-Based Suggestions

Just describe your task naturally:
- "I need to test my web application"
- "Help me create a PDF document"
- "I want to build an MCP server"

Claude will automatically check Context Plane and suggest relevant skills if available.

### Browse Everything

Want to see all available skills?

```bash
/browse-skills
```

## File Locations

```
~/.claude/
├── commands/
│   ├── check-skills.md        # Slash command: check for updates
│   ├── suggest-skill.md       # Slash command: get suggestions
│   └── browse-skills.md       # Slash command: browse all skills
├── skills/
│   ├── context-plane-integration.md  # Auto-integration skill
│   └── installed_skills.json         # Tracks your installed skills
└── hooks/
    ├── context_plane_session_start.sh  # Background: updates manifest
    └── context_plane_session_end.sh    # Background: share modifications
```

## Technical Details

### Background Hooks (Still Running)
The session hooks still run silently in the background:
- **SessionStart**: Updates `installed_skills.json` with latest check timestamp
- **SessionEnd**: Detects skill modifications for sharing

### New Chat-Visible Layer
- **Slash commands**: Run curl commands and display formatted results in chat
- **Automatic suggestions**: Claude queries Context Plane API during conversation
- **Semantic search**: Uses AWS Bedrock Titan embeddings (1024-dimensional vectors)

### API Endpoints Used

```bash
# Check for updates
GET /api/v1/skills/updates?user_id=USER&installed_skills=[]&last_check=TIMESTAMP

# Suggest skills (semantic search)
POST /api/v1/skills/suggest
Body: {"userPrompt": "your task description", "context": {}}

# Get all skills
GET /api/skills

# Get specific skill
GET /api/skills/{skill_id}
```

## Example Workflows

### Workflow 1: Starting Your Day

```bash
# Start Claude Code (session hook runs silently in background)

# Check what's new - this WILL show in chat
/check-skills

# Output:
# "11 new skills available:
#  - MCP Server Development Guide (documentation, v1.0.0)
#  - Web Application Testing (testing, v1.0.0)
#  - PDF Processing Guide (file-processing, v1.0.0)
#  ..."
```

### Workflow 2: Working on a Task

```
You: "I need to test my web application"

Claude: "I can help with that! I notice we have a relevant organizational skill:
        - **Web Application Testing** - Uses Playwright for testing web apps

        Would you like me to write tests using that approach?"

You: "Yes please"

Claude: [Follows the webapp-testing skill guidance to write Playwright tests]
```

### Workflow 3: Exploring Skills

```bash
/browse-skills

# Output shows all skills grouped by category:
# Testing:
#  - Web Application Testing (v1.0.0)
#
# Documentation:
#  - MCP Server Development Guide (v1.0.0)
#  - Skill Creator (v1.0.0)
#
# File Processing:
#  - PDF Processing Guide (v1.0.0)
#  - DOCX creation and editing (v1.0.0)
#  ...
```

## Troubleshooting

### Commands don't show up
```bash
# Restart Claude Code - commands are loaded at startup
# Or check they exist:
ls ~/.claude/commands/
```

### API errors
```bash
# Check if Context Plane is running:
curl http://localhost:8000/api/health

# Should return: {"status":"healthy","service":"Context API","version":"1.0.0"}

# If not, start it:
cd ~/Desktop/context-api
./venv/bin/python main.py
```

### No suggestions appearing
```bash
# Test the API directly:
curl -X POST http://localhost:8000/api/v1/skills/suggest \
  -H "Content-Type: application/json" \
  -d '{"userPrompt":"test my web app","context":{}}'

# Should return suggestions with confidence scores
```

## Comparison: Old vs New

### Old Approach (Silent Hooks)
✅ Runs automatically on session start/end
❌ Output not visible in chat
❌ User doesn't know what's available
✅ Updates manifest in background

### New Approach (Chat Integration)
✅ Visible output in chat
✅ User can manually check anytime (`/check-skills`)
✅ Automatic suggestions during conversation
✅ Interactive and conversational
✅ Still uses background hooks for state management

## Next Steps

1. **Try the commands**: Run `/check-skills` now to see it work
2. **Test automatic suggestions**: Ask Claude to help with a task and see if it suggests relevant skills
3. **Browse skills**: Run `/browse-skills` to see everything available
4. **Give feedback**: Let the team know which skills are useful

## Demo Script (Updated)

For tomorrow's demo, show both layers:

1. **Background layer**: Show `installed_skills.json` being updated (proves hooks work)
2. **Chat layer**: Run `/check-skills` in Claude Code (visible output)
3. **Automatic layer**: Type "I need to test my web app" and watch Claude suggest webapp-testing skill
4. **Semantic search**: Show how it understands intent, not just keywords

## Links

- Context Plane API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- Project: ~/Desktop/context-api
- This Guide: ~/Desktop/context-api/hooks/CHAT_INTEGRATION.md
