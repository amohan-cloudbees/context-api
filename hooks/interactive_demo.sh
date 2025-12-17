#!/bin/bash

# Interactive Context Plane Demo
# Type your prompts and see skill suggestions in real-time

API_ENDPOINT="${CONTEXT_PLANE_API_ENDPOINT:-http://localhost:8000}"

clear
echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  Context Plane - Interactive Skill Suggestion Demo                 ║"
echo "║  Powered by AWS Bedrock Titan Semantic Search                      ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Type a task description and see which skills Context Plane suggests!"
echo ""
echo "Examples to try:"
echo "  - help me test my web application"
echo "  - build a Model Context Protocol server"
echo "  - create a PowerPoint presentation"
echo "  - give me a lucky number"
echo "  - review code for security issues"
echo ""
echo "Type 'quit' or 'exit' to stop"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

while true; do
  # Prompt user for input
  echo -n "Your task → "
  read -r user_prompt

  # Check for exit commands
  if [[ "$user_prompt" == "quit" ]] || [[ "$user_prompt" == "exit" ]] || [[ -z "$user_prompt" ]]; then
    echo ""
    echo "Thanks for using Context Plane! 👋"
    echo ""
    exit 0
  fi

  echo ""
  echo "🔍 Searching for relevant skills using semantic analysis..."
  echo ""

  # Call the suggest endpoint
  RESPONSE=$(curl -s -X POST "$API_ENDPOINT/api/v1/skills/suggest" \
    -H "Content-Type: application/json" \
    -d "{\"userPrompt\":\"$user_prompt\",\"context\":{}}")

  # Check if we got a valid response
  if [ -z "$RESPONSE" ]; then
    echo "❌ Error: Could not connect to Context Plane API"
    echo "   Make sure the server is running at $API_ENDPOINT"
    echo ""
    continue
  fi

  # Count suggestions
  SUGGESTION_COUNT=$(echo "$RESPONSE" | jq -r '.suggestions | length')

  if [ "$SUGGESTION_COUNT" -eq 0 ]; then
    echo "💭 No matching skills found for this task."
    echo ""
  else
    echo "┌────────────────────────────────────────────────────────────────┐"
    echo "│ 💡 Suggested Skills                                             │"
    echo "└────────────────────────────────────────────────────────────────┘"
    echo ""

    # Display each suggestion
    for i in $(seq 0 $((SUGGESTION_COUNT - 1))); do
      SKILL_NAME=$(echo "$RESPONSE" | jq -r ".suggestions[$i].skillMetadata.name")
      CONFIDENCE=$(echo "$RESPONSE" | jq -r ".suggestions[$i].confidence")
      REASONING=$(echo "$RESPONSE" | jq -r ".suggestions[$i].reasoning")
      DESCRIPTION=$(echo "$RESPONSE" | jq -r ".suggestions[$i].skillMetadata.description")
      CATEGORY=$(echo "$RESPONSE" | jq -r ".suggestions[$i].skillMetadata.category")

      echo "  $((i + 1)). 🎯 $SKILL_NAME"
      echo "     📊 Confidence: $CONFIDENCE"
      echo "     📝 Category: $category"
      echo "     💭 $REASONING"
      echo ""
      echo "     Description:"
      echo "     $(echo "$DESCRIPTION" | fold -w 60 -s | sed 's/^/     /')"
      echo ""
    done
  fi

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
done
