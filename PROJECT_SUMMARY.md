# Context Plane API - Project Summary

**Date:** December 15, 2025
**Status:** Demo Ready for December 16
**Tech Stack:** FastAPI, PostgreSQL, AWS Bedrock Titan Embeddings

---

## What We're Building

**Context Plane** is a knowledge base system for AI agent workflows at Unify AI. It manages three types of context artifacts:

1. **Agent Profile Documents (Skills)** - "Resumes" defining AI agent capabilities
2. **Documentation Context** - Runbooks, design docs, coding standards
3. **SDLC State Context** - Real-time development state (PRs, tickets, deployments)

**Current Focus:** Skills system (Type 1) with Claude Code integration via Pre-Hook system.

---

## Architecture Overview

```
Claude Code (User's Machine)
    ↓ HTTP API Calls
Context Plane API (FastAPI)
    ↓ Queries
PostgreSQL Database
    ↓ Embeddings
AWS Bedrock Titan (Semantic Search)
```

**Integration Points:**
1. **SessionStart Hook** - Check for new/updated skills when Claude Code starts
2. **Runtime Suggestions** - Suggest relevant skills based on user's task description
3. **SessionEnd Hook** - Share modified skills with team/organization

---

## What's Built So Far

### Phase 1: Context API Foundation ✅
**Completed:** Earlier sessions (pre-summary)

- Basic Context API with JSONB storage
- User context tracking (repos, tickets, files)
- Added `conversationHistory`, `status`, `blockedBy` fields for AI agent handoff
- Swagger UI with examples
- Database migrations

**Files:**
- `api/routes/context_api.py`
- `api/schemas/context_schema.py`
- `api/services/context_service.py`
- `database/migrations/001-005_*.sql`

---

### Phase 2: Skills System (Type 1 Artifacts) ✅
**Completed:** December 11-12, 2025

**What was built:**
- Skills database model and API endpoints
- Ingestion from Anthropic's skills repository (11 engineering skills)
- Local storage in `skills/` directory with full directory structure
- Test skill: "Lucky Number Generator" for demo purposes

**Skills ingested:**
1. doc-coauthoring
2. docx
3. frontend-design
4. internal-comms
5. mcp-builder
6. pdf
7. pptx
8. skill-creator
9. web-artifacts-builder
10. webapp-testing
11. xlsx
12. lucky-number (custom test skill)

**API Endpoints:**
- `POST /api/skills/ingest` - Ingest skills from local directory
- `GET /api/skills` - Get all skills
- `GET /api/skills/search` - Search skills by query/category/tags
- `GET /api/skills/{skill_id}` - Get specific skill
- `POST /api/skills` - Create custom skill

**Files:**
- `api/models/skill.py` - Skills database model
- `api/schemas/skill_schema.py` - Pydantic schemas
- `api/services/skill_service.py` - Business logic
- `api/routes/skill_routes.py` - API endpoints
- `database/migrations/006_create_skills_table.sql`
- `skills/*/SKILL.md` - 11 skill directories with bundled resources

**Git Commits:**
- `c5c4e5e` - Restructure skills into self-contained directories
- `08f35ce` - Convert skills ingestion from GitHub API to local files

---

### Phase 3: Pre-Hook System v1 (Keyword Matching) ✅
**Completed:** December 15, 2025 (Morning)

**What was built:**
- Three core endpoints for Claude Code integration
- User skills tracking (which skills users have installed)
- Skill version comparison for updates
- Keyword-based skill suggestions

**New Endpoints:**
- `GET /api/v1/skills/updates` - Check for skill updates and new skills
- `POST /api/v1/skills/suggest` - Suggest skills (v1: keyword matching)
- `POST /api/v1/skills/share` - Share modified skills with team/org

**Database Changes:**
- Extended skills table: `version`, `visibility_scope`, `maintainer`, `usage_count`, `changelog_url`, `install_url`
- Created `user_skills` table to track installed skills per user

**Files:**
- `api/models/user_skill.py` - User skills tracking
- `api/routes/prehook_routes.py` - Pre-Hook endpoints
- `api/services/prehook_service.py` - Business logic
- `database/migrations/007_upgrade_skills_table.sql`
- `database/migrations/008_create_user_skills_table.sql`
- `database/migrations/009_add_lucky_number_skill.sql`

**How it worked (v1):**
- User prompt: "review the MCP server"
- Keyword matching finds: "mcp", "server"
- Returns: mcp-builder skill
- Reasoning: "User prompt mentions keywords: mcp, server"

**Git Commit:**
- `001bb3f` - Implement Context Plane Pre-Hook system for Claude Code integration

---

### Phase 4: Semantic Search v2 (AWS Bedrock) ✅
**Completed:** December 15, 2025 (Evening)

**What was built:**
- Upgraded from keyword matching to semantic similarity search
- AWS Bedrock Titan Embeddings integration (1024-dimensional vectors)
- Cosine similarity scoring for relevance ranking
- Automatic fallback to keyword matching if embeddings fail

**Architecture:**
```
User Prompt: "help me test my web application"
    ↓
Bedrock Titan generates embedding (1024 dimensions)
    ↓
Compare with all skill embeddings (cosine similarity)
    ↓
Return top 3 matches sorted by similarity score
```

**Database Changes:**
- Added `embedding` JSONB column to skills table
- All 13 skills have embeddings generated

**Test Results:**
```
Prompt: "help me test my web application"
→ webapp-testing (0.73 confidence)
→ Reasoning: "Semantic similarity score: 0.73 (using Bedrock Titan embeddings)"

Prompt: "build a Model Context Protocol server"
→ mcp-builder (0.62 confidence)

Prompt: "give me a lucky number"
→ lucky-number (0.64 confidence)
```

**Files:**
- `api/services/embedding_service.py` - Bedrock Titan integration
- `scripts/generate_skill_embeddings.py` - Generate embeddings for all skills
- `database/migrations/010_add_skill_embeddings.sql`
- Updated: `api/models/skill.py`, `api/services/prehook_service.py`, `requirements.txt`

**Dependencies Added:**
- `boto3==1.34.0` - AWS SDK
- `pgvector==0.2.4` - Vector operations (using JSONB instead for PG14 compatibility)

**Git Commit:**
- `5f255b6` - Add semantic search v2 using AWS Bedrock Titan Embeddings

---

### Phase 5: Local Hook System for Demo ✅
**Completed:** December 15, 2025 (Night)

**What was built:**
- Complete hook system matching Jason's spec
- Scripts to simulate Claude Code integration
- Demo workflow showing all three integration points

**Files Created:**
```
hooks/
├── README.md                              # Complete documentation
├── setup_local_demo.sh                    # One-time setup
├── demo_workflow.sh                       # Full demo simulation
├── context_plane_session_start.sh         # SessionStart hook
├── context_plane_session_end.sh           # SessionEnd hook
└── claude_settings_template.json          # Claude Code settings
```

**Local Environment Created:**
```
~/.claude/
├── hooks/
│   ├── context_plane_session_start.sh
│   └── context_plane_session_end.sh
└── skills/
    └── installed_skills.json
```

**Demo Flow:**
1. **SessionStart**: Shows notification of 11 new skills available
2. **Runtime**: Demonstrates semantic skill suggestions
3. **SessionEnd**: Shows skill sharing workflow

---

## Current State

### Database Schema

**skills table:**
```sql
- id (UUID, primary key)
- skill_id (VARCHAR, unique)
- title (VARCHAR)
- description (TEXT)
- content (TEXT) - Full markdown
- category (VARCHAR)
- tags (TEXT[])
- source (VARCHAR) - 'anthropic', 'custom'
- source_url (VARCHAR)
- version (VARCHAR) - Semantic version
- visibility_scope (VARCHAR) - 'private', 'team', 'organization', 'global'
- maintainer (VARCHAR)
- usage_count (INTEGER)
- changelog_url (VARCHAR)
- install_url (VARCHAR)
- embedding (JSONB) - 1024-dim vector from Bedrock Titan
- created_at, updated_at (TIMESTAMP)
```

**user_skills table:**
```sql
- id (UUID, primary key)
- user_id (VARCHAR)
- skill_id (VARCHAR)
- installed_version (VARCHAR)
- last_check_timestamp (TIMESTAMP)
- created_at, updated_at (TIMESTAMP)
```

**user_contexts table:**
```sql
- id (UUID, primary key)
- user_id (VARCHAR)
- context_data (JSONB) - stores repoID, catalogID, ticketID, contextLevel,
                          AI_Client_type, details, files, conversationHistory,
                          status, blockedBy
- created_at, updated_at (TIMESTAMP)
```

### API Endpoints Summary

**Context API:**
- `POST /api/context` - Store workflow context
- `GET /api/context/{context_id}` - Retrieve context
- `GET /api/contexts/user/{user_id}` - Get user's contexts
- `GET /api/health` - Health check

**Skills API (Basic):**
- `POST /api/skills/ingest` - Ingest skills from local directory
- `GET /api/skills` - Get all skills
- `GET /api/skills/search` - Search skills
- `GET /api/skills/{skill_id}` - Get specific skill
- `POST /api/skills` - Create custom skill

**Pre-Hook API:**
- `GET /api/v1/skills/updates` - Check for updates
- `POST /api/v1/skills/suggest` - Suggest skills (semantic v2)
- `POST /api/v1/skills/share` - Share modifications

### Skills in Database

**Total:** 13 skills (all with Bedrock Titan embeddings)

**Engineering Skills (from Anthropic):**
1. doc-coauthoring - Document collaboration workflow
2. docx - DOCX creation and editing
3. frontend-design - UI/UX design assistance
4. internal-comms - Internal communication help
5. mcp-builder - MCP server development
6. pdf - PDF processing
7. pptx - PowerPoint creation
8. skill-creator - Create new skills
9. web-artifacts-builder - Build web artifacts
10. webapp-testing - Playwright testing
11. xlsx - Excel processing

**Custom Skills:**
12. lucky-number - Test skill (returns random number 1-999)
13. lucky-number-context-plane-team - Shared team version

### Current Limitations

**Not Yet Implemented:**
- Documentation Context (Type 2 artifacts)
- SDLC State Context (Type 3 artifacts)
- Real Claude Code integration (only simulated via hooks)
- Unify-specific skills (have generic Anthropic skills)
- Actual script execution from skills
- Vector search optimization (using JSONB, not pgvector due to PG14 compatibility)
- User authentication/authorization
- Team/organization management

---

## Technology Stack

### Backend
- **FastAPI** 0.104.1 - Web framework
- **SQLAlchemy** 2.0.23 - ORM
- **PostgreSQL** 14 - Database
- **Pydantic** 2.5.0 - Data validation

### AI/ML
- **AWS Bedrock Titan Embeddings** - Semantic search
- **boto3** 1.34.0 - AWS SDK
- **NumPy** - Vector operations

### Development
- **Uvicorn** - ASGI server
- **pytest** - Testing
- **Git** - Version control

---

## How to Run

### 1. Start Server
```bash
cd /Users/achinthalapalli/Desktop/context-api
./venv/bin/python main.py
```

Server runs at: http://localhost:8000
Swagger UI: http://localhost:8000/docs

### 2. Run Demo
```bash
cd hooks
./demo_workflow.sh
```

### 3. Test Individual Components

**Test Semantic Search:**
```bash
curl -X POST http://localhost:8000/api/v1/skills/suggest \
  -H "Content-Type: application/json" \
  -d '{"userPrompt":"help me test my web application","context":{}}'
```

**Test Updates Check:**
```bash
curl "http://localhost:8000/api/v1/skills/updates?user_id=test-user&installed_skills=%5B%7B%22skill_id%22%3A%22pdf%22%2C%22version%22%3A%220.9.0%22%7D%5D&last_check=2024-01-01T00:00:00Z"
```

**Test SessionStart Hook:**
```bash
~/.claude/hooks/context_plane_session_start.sh
```

---

## Demo Script for Tomorrow

### Setup (5 minutes before)
```bash
# 1. Start the server
cd /Users/achinthalapalli/Desktop/context-api
./venv/bin/python main.py

# 2. Verify it's running
curl http://localhost:8000/
```

### Demo Flow (10-15 minutes)

**Part 1: Show the Problem (2 min)**
- AI agents need to know organizational context
- Skills define what agents can do
- Need to discover and share skills across teams

**Part 2: Pre-Hook System Overview (3 min)**
- Show Jason's spec: `context-plane-prehook-spec.md`
- Explain three integration points:
  1. SessionStart - Check for updates
  2. Runtime - Suggest relevant skills
  3. SessionEnd - Share modifications

**Part 3: Live Demo (5 min)**
```bash
cd hooks
./demo_workflow.sh
```

Walk through each step:
- SessionStart notification shows new skills
- Runtime suggestions use semantic search (show Bedrock Titan)
- SessionEnd offers to share modifications

**Part 4: Show Semantic Search Upgrade (3 min)**

Compare v1 vs v2:

```bash
# v2 (Semantic) - Better understanding
curl -X POST http://localhost:8000/api/v1/skills/suggest \
  -H "Content-Type: application/json" \
  -d '{"userPrompt":"I want to test my website","context":{}}'
```

Show reasoning:
- v1: "Keywords match: test, website"
- v2: "Semantic similarity: 0.73 (Bedrock Titan)"

**Part 5: Swagger UI Walkthrough (2 min)**
- Open http://localhost:8000/docs
- Show all Pre-Hook endpoints
- Try live query in Swagger

### Key Points to Emphasize
1. ✅ **Working semantic search** with AWS Bedrock Titan
2. ✅ **All three integration points** implemented
3. ✅ **13 skills with embeddings** ready to use
4. ✅ **Automatic fallback** to keyword matching
5. ✅ **Version tracking** for skill updates
6. ✅ **Team sharing** for collaboration

---

## Key Decisions Made

### Technical Decisions
1. **JSONB over pgvector**: Used JSONB to store embeddings for PostgreSQL 14 compatibility
2. **AWS Bedrock Titan**: Chose over OpenAI for existing AWS setup
3. **Local file storage**: Skills stored in `skills/` directories instead of GitHub API
4. **Keyword fallback**: Automatic fallback if embeddings fail
5. **example.com URLs**: Used for placeholder changelog/install URLs

### Architecture Decisions
1. **Model 2 (Smart Router)**: Context Plane does semantic matching, not just storage
2. **Generic + Custom Skills**: Keep Anthropic skills, add custom ones later
3. **Three-phase approach**: Basic → Pre-Hooks → Semantic Search
4. **FastAPI**: Chosen for speed and auto-generated Swagger docs

### Scope Decisions
1. **Phase 1 Focus**: Skills only (not Doc Context or SDLC Context yet)
2. **Demo-first**: Prioritize working demo over production features
3. **No authentication**: Skip for demo, add later
4. **Simulated hooks**: Create bash scripts instead of actual Claude Code integration

---

## What's Next (Post-Demo)

### Immediate (Week 1)
- [ ] Create Unify-specific skills (coding standards, runbooks)
- [ ] Add user authentication and team management
- [ ] Deploy to AWS/staging environment
- [ ] Integrate with actual Claude Code (not simulated)

### Short-term (Month 1)
- [ ] Documentation Context (Type 2) with vector search
- [ ] SDLC State Context (Type 3) - GitHub/Jira integration
- [ ] Skill execution framework (run scripts from skills)
- [ ] Analytics dashboard for skill usage

### Long-term (Quarter 1)
- [ ] AI-powered skill recommendations
- [ ] Skill marketplace/ratings
- [ ] Skill composition (combine multiple skills)
- [ ] Multi-model embedding support

---

## Files Structure

```
context-api/
├── api/
│   ├── models/
│   │   ├── context.py           # Context database model
│   │   ├── skill.py             # Skills database model
│   │   └── user_skill.py        # User skills tracking
│   ├── routes/
│   │   ├── context_api.py       # Context endpoints
│   │   ├── skill_routes.py      # Skills endpoints
│   │   └── prehook_routes.py    # Pre-Hook endpoints
│   ├── schemas/
│   │   ├── context_schema.py    # Context validation schemas
│   │   └── skill_schema.py      # Skills validation schemas
│   └── services/
│       ├── context_service.py   # Context business logic
│       ├── skill_service.py     # Skills business logic
│       ├── prehook_service.py   # Pre-Hook business logic
│       └── embedding_service.py # Bedrock Titan integration
├── config/
│   ├── database.py              # Database connection
│   └── settings.py              # Application settings
├── database/
│   └── migrations/              # SQL migration files (001-010)
├── hooks/
│   ├── README.md                # Hook system documentation
│   ├── setup_local_demo.sh      # Setup script
│   ├── demo_workflow.sh         # Demo simulation
│   ├── context_plane_session_start.sh
│   ├── context_plane_session_end.sh
│   └── claude_settings_template.json
├── scripts/
│   └── generate_skill_embeddings.py  # Generate embeddings
├── skills/                      # 11 skill directories
│   ├── doc-coauthoring/
│   ├── mcp-builder/
│   ├── webapp-testing/
│   └── ... (8 more)
├── main.py                      # FastAPI application
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
└── PROJECT_SUMMARY.md          # This file
```

---

## Environment Variables

```bash
# .env file
DATABASE_URL=postgresql://achinthalapalli:@localhost:5432/context_db
APP_NAME=Context API
APP_VERSION=1.0.0
DEBUG=true
HOST=0.0.0.0
PORT=8000

# AWS Credentials (for Bedrock)
AWS_PROFILE=default  # Or use AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
AWS_REGION=us-east-1
```

---

## Git History

```
5f255b6 (HEAD -> main, origin/main) Add semantic search v2 using AWS Bedrock Titan Embeddings
001bb3f Implement Context Plane Pre-Hook system for Claude Code integration
c5c4e5e Restructure skills into self-contained directories
08f35ce Convert skills ingestion from GitHub API to local files
... (earlier commits for Context API foundation)
```

---

## Reference Documents

1. **ContextPLTC.md** - Original specification defining 3 artifact types
2. **context-plane-prehook-spec.md** - Jason's spec for Claude Code integration
3. **hooks/README.md** - Complete hook system documentation
4. **PROJECT_SUMMARY.md** - This file

---

## Contact/Questions

- **Repository**: github.com/amohan-cloudbees/context-api
- **Manager**: Jason (provided Pre-Hook spec)
- **Tech Stack Questions**: Check requirements.txt
- **Architecture Questions**: See ContextPLTC.md

---

## Quick Reference Commands

```bash
# Start server
./venv/bin/python main.py

# Run demo
cd hooks && ./demo_workflow.sh

# Test semantic search
curl -X POST http://localhost:8000/api/v1/skills/suggest \
  -H "Content-Type: application/json" \
  -d '{"userPrompt":"your query here","context":{}}'

# Regenerate embeddings
./venv/bin/python scripts/generate_skill_embeddings.py

# Check database
psql -h localhost -U achinthalapalli -d context_db

# View logs
tail -f logs/app.log

# Run migrations
psql -h localhost -U achinthalapalli -d context_db -f database/migrations/XXX_*.sql
```

---

**Status:** ✅ DEMO READY - December 16, 2025

All core features working. Semantic search with AWS Bedrock operational. Hook system simulating Claude Code integration. Ready to demonstrate to stakeholders.
