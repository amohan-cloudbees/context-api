#!/bin/bash

# Setup script for Context Plane local demo
# This sets up the hook system to work with Claude Code

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  Context Plane Pre-Hook Setup                                      ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Create Claude directories
CLAUDE_DIR="$HOME/.claude"
HOOKS_DIR="$CLAUDE_DIR/hooks"
SKILLS_DIR="$CLAUDE_DIR/skills"
COMMANDS_DIR="$CLAUDE_DIR/commands"

echo "Creating directories..."
mkdir -p "$HOOKS_DIR"
mkdir -p "$SKILLS_DIR"
mkdir -p "$COMMANDS_DIR"

# Copy hook scripts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing hook scripts..."
cp "$SCRIPT_DIR/context_plane_session_start.sh" "$HOOKS_DIR/"
cp "$SCRIPT_DIR/context_plane_session_end.sh" "$HOOKS_DIR/"

# Make scripts executable
chmod +x "$HOOKS_DIR/context_plane_session_start.sh"
chmod +x "$HOOKS_DIR/context_plane_session_end.sh"

echo "Installing slash commands..."
cp "$SCRIPT_DIR/commands/"*.md "$COMMANDS_DIR/"

echo "Installing Context Plane integration skill..."
cp "$SCRIPT_DIR/context-plane-integration.md" "$SKILLS_DIR/"

# Initialize skills manifest
SKILLS_MANIFEST="$SKILLS_DIR/installed_skills.json"
if [ ! -f "$SKILLS_MANIFEST" ]; then
  echo "Initializing skills manifest..."
  cat > "$SKILLS_MANIFEST" << 'EOF'
{
  "installedSkills": [
    {"skill_id": "webapp-testing", "version": "0.9.0"},
    {"skill_id": "pdf", "version": "0.8.0"}
  ],
  "lastUpdateCheck": "2024-01-01T00:00:00Z"
}
EOF
fi

# Set environment variable
export CONTEXT_PLANE_API_ENDPOINT="http://localhost:8000"

echo ""
echo "✓ Setup complete!"
echo ""
echo "Directory structure created:"
echo "  ~/.claude/hooks/context_plane_session_start.sh"
echo "  ~/.claude/hooks/context_plane_session_end.sh"
echo "  ~/.claude/commands/browse-skills.md"
echo "  ~/.claude/commands/check-skills.md"
echo "  ~/.claude/commands/suggest-skill.md"
echo "  ~/.claude/skills/context-plane-integration.md"
echo "  ~/.claude/skills/installed_skills.json"
echo ""
echo "✓ Slash commands installed:"
echo "  /browse-skills - Browse new skills you don't have"
echo "  /check-skills  - Check for updates since last session"
echo "  /suggest-skill - Get AI-powered skill recommendations"
echo ""
echo "To configure Claude Code, add this to your Claude settings:"
echo "  File: ~/.claude/settings.json"
echo ""
echo "  See: hooks/claude_settings_template.json for example"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "⚠️  IMPORTANT: Restart Claude Code to load the slash commands"
echo ""
echo "To test the hook system, run:"
echo "  ./hooks/demo_workflow.sh"
echo ""
