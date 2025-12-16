#!/bin/bash

# Demo script showing the complete Context Plane Pre-Hook workflow
# This simulates what happens during a Claude Code session

API_ENDPOINT="${CONTEXT_PLANE_API_ENDPOINT:-http://localhost:8000}"
SKILLS_DIR="$HOME/.claude/skills"
SKILLS_MANIFEST="$SKILLS_DIR/installed_skills.json"

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  Context Plane Pre-Hook Demo                                       ║"
echo "║  Simulating Claude Code Integration                                ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Demo Step 1: Session Start
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: SessionStart Hook (Checking for skill updates)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run session start hook
"$HOME/.claude/hooks/context_plane_session_start.sh"

echo ""
read -p "Press Enter to continue to Step 2..."
echo ""

# Demo Step 2: Runtime Suggestion
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Runtime Skill Suggestion (During task execution)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "User asks: 'Help me test my web application'"
echo ""
echo "Context Plane suggests relevant skills..."
echo ""

# Query suggest endpoint
RESPONSE=$(curl -s -X POST "$API_ENDPOINT/api/v1/skills/suggest" \
  -H "Content-Type: application/json" \
  -d '{"userPrompt":"help me test my web application","context":{}}')

echo "┌────────────────────────────────────────────────────────────┐"
echo "│ 💡 Suggested Skill from Context Plane                      │"
echo "└────────────────────────────────────────────────────────────┘"
echo ""

# Parse and display suggestion
SKILL_NAME=$(echo "$RESPONSE" | jq -r '.suggestions[0].skillMetadata.name // "None"')
CONFIDENCE=$(echo "$RESPONSE" | jq -r '.suggestions[0].confidence // 0')
REASONING=$(echo "$RESPONSE" | jq -r '.suggestions[0].reasoning // "No suggestions"')

if [ "$SKILL_NAME" != "None" ]; then
  echo "  🔧 $SKILL_NAME"
  echo "  📊 Confidence: $CONFIDENCE"
  echo "  💭 $REASONING"
  echo ""
  echo "  [Use This Skill] [Not Now] [Details]"
else
  echo "  No matching skills found"
fi

echo ""
read -p "Press Enter to continue to Step 3..."
echo ""

# Demo Step 3: Additional Examples
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: More Skill Suggestion Examples"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Example queries
QUERIES=(
  "give me a lucky number"
  "help me build a Model Context Protocol server"
  "create a PowerPoint presentation"
)

for query in "${QUERIES[@]}"; do
  echo "Query: \"$query\""

  RESPONSE=$(curl -s -X POST "$API_ENDPOINT/api/v1/skills/suggest" \
    -H "Content-Type: application/json" \
    -d "{\"userPrompt\":\"$query\",\"context\":{}}")

  SKILL_NAME=$(echo "$RESPONSE" | jq -r '.suggestions[0].skillMetadata.name // "None"')
  CONFIDENCE=$(echo "$RESPONSE" | jq -r '.suggestions[0].confidence // 0')

  if [ "$SKILL_NAME" != "None" ]; then
    echo "  → Suggested: $SKILL_NAME (confidence: $CONFIDENCE)"
  else
    echo "  → No suggestions"
  fi
  echo ""
done

read -p "Press Enter to continue to Step 4..."
echo ""

# Demo Step 4: Skill Sharing
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: SessionEnd Hook (Sharing skill modifications)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "User modified 'Lucky Number' skill during session..."
echo ""
echo "Sharing modification with team..."
echo ""

SHARE_RESPONSE=$(curl -s -X POST "$API_ENDPOINT/api/v1/skills/share" \
  -H "Content-Type: application/json" \
  -d '{
    "skillId": "lucky-number",
    "baseVersion": "1.0.0",
    "modifiedVersion": "1.1.0",
    "changes": {
      "diff": "Added extra luck features",
      "changelog": "Improved luck algorithm for better numbers",
      "filesModified": ["lucky.py"]
    },
    "shareScope": "team",
    "teamId": "context-plane-team",
    "notifyUsers": true
  }')

echo "┌────────────────────────────────────────────────────────────┐"
echo "│ ✓ Skill Update Shared                                      │"
echo "└────────────────────────────────────────────────────────────┘"
echo ""

SHARED_ID=$(echo "$SHARE_RESPONSE" | jq -r '.sharedSkillId // "unknown"')
NOTIFIED=$(echo "$SHARE_RESPONSE" | jq -r '.notifiedUsers // 0')

echo "  Shared Skill: $SHARED_ID"
echo "  Team Members Notified: $NOTIFIED"
echo ""

# Run session end hook
"$HOME/.claude/hooks/context_plane_session_end.sh"

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  Demo Complete!                                                    ║"
echo "╠════════════════════════════════════════════════════════════════════╣"
echo "║                                                                    ║"
echo "║  This demonstrated the three Context Plane integration points:    ║"
echo "║                                                                    ║"
echo "║  1. SessionStart: Check for new skills                            ║"
echo "║  2. Runtime: Suggest relevant skills during task execution        ║"
echo "║  3. SessionEnd: Share skill modifications with team               ║"
echo "║                                                                    ║"
echo "║  All using semantic search powered by AWS Bedrock Titan!          ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
