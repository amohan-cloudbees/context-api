# Context Plane Pre-Hook System - Local Demo

This directory contains the hook system for integrating Context Plane with Claude Code locally, as specified in Jason's `context-plane-prehook-spec.md`.

## Quick Start

### 1. Setup (One-time)

```bash
# Run the setup script
cd hooks
./setup_local_demo.sh
```

This creates:
- `~/.claude/hooks/` - Hook scripts
- `~/.claude/skills/` - Local skills directory
- `~/.claude/skills/installed_skills.json` - Tracks installed skills

### 2. Run Demo

```bash
# Make sure your Context API server is running
cd /Users/achinthalapalli/Desktop/context-api
./venv/bin/python main.py

# In another terminal, run the demo
cd hooks
./demo_workflow.sh
```

## How It Works

### Three Integration Points

#### 1. SessionStart Hook
**When**: Claude Code session begins
**What**: Checks Context Plane API for new/updated skills
**Hook**: `~/.claude/hooks/context_plane_session_start.sh`

```bash
# Simulates Claude Code starting
~/.claude/hooks/context_plane_session_start.sh
```

Shows notification like:
```
╔════════════════════════════════════════════════════════════════════╗
║  🎯 New Skills Available (3)                                       ║
╠════════════════════════════════════════════════════════════════════╣
║  📦 Lucky Number Generator                                         ║
║     Returns a random lucky number between 1 and 999                ║
║     Category: testing | Version: 1.0.0                             ║
╚════════════════════════════════════════════════════════════════════╝
```

#### 2. Runtime Skill Suggestion
**When**: User describes a task during coding
**What**: Context Plane suggests relevant skills using semantic search
**Endpoint**: `POST /api/v1/skills/suggest`

```bash
# Test manually
curl -X POST http://localhost:8000/api/v1/skills/suggest \
  -H "Content-Type: application/json" \
  -d '{"userPrompt":"help me test my web application","context":{}}'
```

Returns:
```json
{
  "suggestions": [
    {
      "skillId": "webapp-testing",
      "confidence": 0.73,
      "reasoning": "Semantic similarity score: 0.73 (using Bedrock Titan embeddings)",
      "skillMetadata": {
        "name": "Web Application Testing",
        "description": "To test local web applications, write native Python Playwright scripts.",
        "category": "testing"
      }
    }
  ]
}
```

#### 3. SessionEnd Hook
**When**: Claude Code session ends
**What**: Offers to share modified skills with team
**Hook**: `~/.claude/hooks/context_plane_session_end.sh`

## Files

```
hooks/
├── README.md                              # This file
├── setup_local_demo.sh                    # One-time setup script
├── demo_workflow.sh                       # Full demo simulation
├── context_plane_session_start.sh         # SessionStart hook
├── context_plane_session_end.sh           # SessionEnd hook
└── claude_settings_template.json          # Claude Code settings example
```

## Configuration

### Environment Variables

```bash
# Set Context Plane API endpoint (default: http://localhost:8000)
export CONTEXT_PLANE_API_ENDPOINT="http://localhost:8000"

# Or add to ~/.bashrc or ~/.zshrc
echo 'export CONTEXT_PLANE_API_ENDPOINT="http://localhost:8000"' >> ~/.zshrc
```

### Claude Code Settings

To integrate with actual Claude Code, add to `~/.claude/settings.json`:

```json
{
  "contextPlane": {
    "enabled": true,
    "apiEndpoint": "http://localhost:8000"
  },
  "hooks": {
    "sessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/context_plane_session_start.sh"
          }
        ]
      }
    ],
    "sessionEnd": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/context_plane_session_end.sh"
          }
        ]
      }
    ]
  }
}
```

## Demo Scenarios

### Scenario 1: Web Testing
```bash
# User prompt
"help me test my web application"

# Context Plane suggests
→ Web Application Testing skill (0.73 confidence)
→ Uses Bedrock Titan semantic embeddings
```

### Scenario 2: MCP Development
```bash
# User prompt
"build a Model Context Protocol server"

# Context Plane suggests
→ MCP Server Development Guide (0.62 confidence)
```

### Scenario 3: Lucky Number
```bash
# User prompt
"give me a lucky number"

# Context Plane suggests
→ Lucky Number Generator (0.64 confidence)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Claude Code (User's Machine)                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  SessionStart Hook                                     │ │
│  │  • Runs on startup                                     │ │
│  │  • Checks ~/.claude/skills/installed_skills.json      │ │
│  │  • Queries Context Plane API for updates              │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Runtime (During Coding)                               │ │
│  │  • User describes task                                 │ │
│  │  • Context Plane suggests skills (semantic search)    │ │
│  │  • User accepts/rejects suggestion                     │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  SessionEnd Hook                                       │ │
│  │  • Detects skill modifications                         │ │
│  │  • Offers to share with team                           │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP API
┌─────────────────────────────────────────────────────────────┐
│  Context Plane API (localhost:8000)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Skills Database (PostgreSQL)                          │ │
│  │  • 13 skills with Bedrock Titan embeddings             │ │
│  │  • Semantic search via cosine similarity               │ │
│  │  • Version tracking & sharing                          │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  AWS Bedrock Titan Embeddings                          │ │
│  │  • 1024-dimensional vectors                            │ │
│  │  • Semantic understanding of user prompts              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Testing Individual Hooks

```bash
# Test SessionStart hook
~/.claude/hooks/context_plane_session_start.sh

# Test SessionEnd hook
~/.claude/hooks/context_plane_session_end.sh

# Test skill suggestion directly
curl -X POST http://localhost:8000/api/v1/skills/suggest \
  -H "Content-Type: application/json" \
  -d '{"userPrompt":"your task here","context":{}}'

# Test skill sharing
curl -X POST http://localhost:8000/api/v1/skills/share \
  -H "Content-Type: application/json" \
  -d '{
    "skillId": "lucky-number",
    "baseVersion": "1.0.0",
    "modifiedVersion": "1.1.0",
    "changes": {
      "diff": "improvements",
      "changelog": "Made it better",
      "filesModified": ["lucky.py"]
    },
    "shareScope": "team",
    "teamId": "my-team",
    "notifyUsers": true
  }'
```

## Troubleshooting

### Hook not running?
```bash
# Check if hook script is executable
ls -la ~/.claude/hooks/context_plane_session_start.sh

# Should show: -rwxr-xr-x (executable)
# If not: chmod +x ~/.claude/hooks/context_plane_session_start.sh
```

### API not responding?
```bash
# Check if server is running
curl http://localhost:8000/

# Should return: {"name":"Context API","version":"1.0.0",...}
```

### No skills showing?
```bash
# Check if embeddings exist
curl http://localhost:8000/api/skills | jq '.[0].embedding'

# Should return an array of numbers (embedding vector)
# If null, run: ./venv/bin/python scripts/generate_skill_embeddings.py
```

## Next Steps

1. **For Demo Tomorrow**: Run `./demo_workflow.sh` - shows complete flow
2. **For Real Integration**: Configure Claude Code with the settings template
3. **Add More Skills**: Use POST /api/skills endpoint or modify skills/ directory

## Reference

Based on: `context-plane-prehook-spec.md` by Jason
- SessionStart: Notification system for new skills
- Runtime: Semantic skill suggestions during coding
- SessionEnd: Team collaboration via skill sharing
