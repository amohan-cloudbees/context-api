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

echo "Creating directories..."
mkdir -p "$HOOKS_DIR"
mkdir -p "$SKILLS_DIR"

# Copy hook scripts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing hook scripts..."
cp "$SCRIPT_DIR/context_plane_session_start.sh" "$HOOKS_DIR/"
cp "$SCRIPT_DIR/context_plane_session_end.sh" "$HOOKS_DIR/"

# Make scripts executable
chmod +x "$HOOKS_DIR/context_plane_session_start.sh"
chmod +x "$HOOKS_DIR/context_plane_session_end.sh"

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
echo "  ~/.claude/skills/installed_skills.json"
echo ""
echo "To configure Claude Code, add this to your Claude settings:"
echo "  File: ~/.claude/settings.json"
echo ""
echo "  See: hooks/claude_settings_template.json for example"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "To test the hook system, run:"
echo "  ./hooks/demo_workflow.sh"
echo ""
