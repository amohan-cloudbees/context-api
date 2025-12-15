-- Migration: Upgrade skills table for Context Plane Pre-Hook system
-- Adds version tracking, visibility scoping, and usage analytics

-- Add new columns to skills table
ALTER TABLE skills
ADD COLUMN IF NOT EXISTS version VARCHAR(50) DEFAULT '1.0.0',
ADD COLUMN IF NOT EXISTS visibility_scope VARCHAR(20) DEFAULT 'organization',
ADD COLUMN IF NOT EXISTS maintainer VARCHAR(255),
ADD COLUMN IF NOT EXISTS usage_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS changelog_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS install_url VARCHAR(500);

-- Add check constraint for visibility_scope
ALTER TABLE skills
ADD CONSTRAINT skills_visibility_scope_check
CHECK (visibility_scope IN ('private', 'team', 'organization', 'global'));

-- Create index for visibility_scope filtering
CREATE INDEX IF NOT EXISTS idx_skills_visibility_scope ON skills(visibility_scope);

-- Create index for version
CREATE INDEX IF NOT EXISTS idx_skills_version ON skills(version);

-- Create index for maintainer
CREATE INDEX IF NOT EXISTS idx_skills_maintainer ON skills(maintainer);

-- Update existing skills with default values
UPDATE skills
SET
    version = '1.0.0',
    visibility_scope = 'organization',
    maintainer = 'anthropic',
    usage_count = 0
WHERE version IS NULL;

COMMENT ON COLUMN skills.version IS 'Semantic version of the skill (e.g., 1.2.0)';
COMMENT ON COLUMN skills.visibility_scope IS 'Access level: private, team, organization, global';
COMMENT ON COLUMN skills.maintainer IS 'Team or individual maintaining this skill';
COMMENT ON COLUMN skills.usage_count IS 'Number of times this skill has been activated';
COMMENT ON COLUMN skills.changelog_url IS 'URL to skill changelog documentation';
COMMENT ON COLUMN skills.install_url IS 'URL for installing/viewing this skill';
