# Claude Code Slash Commands

This directory contains Claude Code slash commands that provide the user interface for the Context Plane API.

## Available Commands

- **`/browse-skills`** - Browse new skills you don't have installed yet
- **`/check-skills`** - Check for new skills and updates since your last session
- **`/suggest-skill`** - Get AI-powered skill recommendations for your task

## Installation

These commands are automatically installed by the setup script:

```bash
cd hooks
./setup_local_demo.sh
```

Or manually:

```bash
mkdir -p ~/.claude/commands
cp hooks/commands/*.md ~/.claude/commands/
```

## Usage

After installation, restart Claude Code and use the commands by typing them in chat:
- `/browse-skills`
- `/check-skills`
- `/suggest-skill`

## See Also

Refer to the main [README.md](../../README.md) for complete setup and usage documentation.
