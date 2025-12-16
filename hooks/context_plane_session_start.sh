#!/bin/bash

# Context Plane Session Start Hook
# Checks for skill updates and displays notifications

API_ENDPOINT="${CONTEXT_PLANE_API_ENDPOINT:-http://localhost:8000}"
USER_ID="${USER:-$(whoami)}"
SKILLS_DIR="$HOME/.claude/skills"
SKILLS_MANIFEST="$SKILLS_DIR/installed_skills.json"

# Ensure skills directory exists
mkdir -p "$SKILLS_DIR"

# Initialize manifest if it doesn't exist
if [ ! -f "$SKILLS_MANIFEST" ]; then
  echo '{"installedSkills": [], "lastUpdateCheck": "2000-01-01T00:00:00Z"}' > "$SKILLS_MANIFEST"
fi

# Get last check timestamp and installed skills
LAST_CHECK=$(jq -r '.lastUpdateCheck // "2000-01-01T00:00:00Z"' "$SKILLS_MANIFEST")
INSTALLED_SKILLS=$(jq -c '.installedSkills // []' "$SKILLS_MANIFEST")

# Query API for updates
RESPONSE=$(curl -s -G "$API_ENDPOINT/api/v1/skills/updates" \
  --data-urlencode "user_id=$USER_ID" \
  --data-urlencode "installed_skills=$INSTALLED_SKILLS" \
  --data-urlencode "last_check=$LAST_CHECK")

# Parse response
AVAILABLE_UPDATES=$(echo "$RESPONSE" | jq -r '.availableUpdates // [] | length')
NEW_SKILLS=$(echo "$RESPONSE" | jq -r '.newSkills // [] | length')
TOTAL_COUNT=$((AVAILABLE_UPDATES + NEW_SKILLS))

if [ "$TOTAL_COUNT" -gt 0 ]; then
  echo ""
  echo "╔════════════════════════════════════════════════════════════════════╗"
  echo "║  🎯 New Skills Available ($TOTAL_COUNT)                                        ║"
  echo "╠════════════════════════════════════════════════════════════════════╣"
  echo "║                                                                    ║"
  echo "║  Your organization has published new skills since your last        ║"
  echo "║  session:                                                          ║"
  echo "║                                                                    ║"

  # Display new skills
  echo "$RESPONSE" | jq -r '.newSkills[] |
    "║  📦 \(.name)\n║     \(.description)\n║     Category: \(.category) | Version: \(.latestVersion)\n║     "' | head -20

  # Display updates
  if [ "$AVAILABLE_UPDATES" -gt 0 ]; then
    echo "$RESPONSE" | jq -r '.availableUpdates[] |
      "║  🔄 \(.name) - Update Available\n║     \(.currentVersion) → \(.latestVersion)\n║     "' | head -10
  fi

  echo "║  View all: $API_ENDPOINT/api/skills                               ║"
  echo "║                                                                    ║"
  echo "╚════════════════════════════════════════════════════════════════════╝"
  echo ""
fi

# Update last check timestamp
jq --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '.lastUpdateCheck = $timestamp' \
  "$SKILLS_MANIFEST" > "${SKILLS_MANIFEST}.tmp" && \
  mv "${SKILLS_MANIFEST}.tmp" "$SKILLS_MANIFEST"

exit 0
