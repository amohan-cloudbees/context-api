-- Migration: Create user_skills table for tracking installed skills
-- Tracks which skills each user has installed and their versions

CREATE TABLE IF NOT EXISTS user_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    skill_id VARCHAR(255) NOT NULL,
    installed_version VARCHAR(50) NOT NULL,
    last_check_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Ensure unique user-skill combination
    CONSTRAINT user_skills_unique UNIQUE (user_id, skill_id)
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_user_skills_user_id ON user_skills(user_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_skill_id ON user_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_last_check ON user_skills(last_check_timestamp);

-- Comments
COMMENT ON TABLE user_skills IS 'Tracks which skills each user has installed';
COMMENT ON COLUMN user_skills.user_id IS 'User identifier (from Claude Code)';
COMMENT ON COLUMN user_skills.skill_id IS 'Skill identifier';
COMMENT ON COLUMN user_skills.installed_version IS 'Version of skill user has installed';
COMMENT ON COLUMN user_skills.last_check_timestamp IS 'Last time user checked for updates';
