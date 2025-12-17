#!/bin/bash

# Context Plane Skill Installation Script
# Downloads and installs skills from Context Plane API to Claude Code

set -e

API_ENDPOINT="${CONTEXT_PLANE_API_ENDPOINT:-http://localhost:8000}"
SKILLS_DIR="$HOME/.claude/skills"
SKILLS_MANIFEST="$SKILLS_DIR/installed_skills.json"

# Ensure skills directory exists
mkdir -p "$SKILLS_DIR"

# Initialize manifest if it doesn't exist
if [ ! -f "$SKILLS_MANIFEST" ]; then
  echo '{"installedSkills": [], "lastUpdateCheck": "2000-01-01T00:00:00Z"}' > "$SKILLS_MANIFEST"
fi

# Function to install a skill
install_skill() {
  local skill_id="$1"

  echo "📦 Downloading skill: $skill_id"

  # Fetch skill details from API
  RESPONSE=$(curl -s "$API_ENDPOINT/api/skills/$skill_id")

  # Check if skill exists
  if echo "$RESPONSE" | jq -e '.status == "error"' > /dev/null 2>&1; then
    echo "❌ Error: Skill '$skill_id' not found in Context Plane"
    return 1
  fi

  # Extract skill data
  SKILL_CONTENT=$(echo "$RESPONSE" | jq -r '.content // ""')
  SKILL_VERSION=$(echo "$RESPONSE" | jq -r '.version // "1.0.0"')
  SKILL_NAME=$(echo "$RESPONSE" | jq -r '.title // .skillId')

  if [ -z "$SKILL_CONTENT" ] || [ "$SKILL_CONTENT" = "null" ]; then
    echo "❌ Error: Skill content is empty"
    return 1
  fi

  # Save skill to file (using skillId as filename)
  SKILL_FILE="$SKILLS_DIR/${skill_id}.md"
  echo "$SKILL_CONTENT" > "$SKILL_FILE"

  # Update installed_skills.json
  TMP_FILE=$(mktemp)
  jq --arg skill_id "$skill_id" --arg version "$SKILL_VERSION" \
    '.installedSkills |= (map(select(.skill_id != $skill_id)) + [{skill_id: $skill_id, version: $version}])' \
    "$SKILLS_MANIFEST" > "$TMP_FILE" && mv "$TMP_FILE" "$SKILLS_MANIFEST"

  echo "✅ Installed: $SKILL_NAME (v$SKILL_VERSION)"
  echo "   Location: $SKILL_FILE"

  return 0
}

# Main script logic
if [ $# -eq 0 ]; then
  echo "Usage: $0 <skill-id> [skill-id2 ...]"
  echo ""
  echo "Example:"
  echo "  $0 lucky-number"
  echo "  $0 webapp-testing pdf docx"
  echo ""
  echo "Available skills:"
  curl -s "$API_ENDPOINT/api/skills" | jq -r '.data[] | "  - \(.skillId): \(.title)"'
  exit 1
fi

# Install each skill
SUCCESS_COUNT=0
FAIL_COUNT=0

for skill_id in "$@"; do
  if install_skill "$skill_id"; then
    ((SUCCESS_COUNT++))
  else
    ((FAIL_COUNT++))
  fi
  echo ""
done

# Summary
echo "═══════════════════════════════════════"
echo "Installation complete!"
echo "  ✅ Success: $SUCCESS_COUNT"
echo "  ❌ Failed: $FAIL_COUNT"
echo ""
echo "Skills directory: $SKILLS_DIR"
echo "═══════════════════════════════════════"

exit 0
