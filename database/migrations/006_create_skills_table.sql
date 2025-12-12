-- Migration: Create skills table for Agent Profile Documents (Context Artifact Type 1)
-- Date: 2024-12-12
-- Description: Table for storing agent skills/profiles from Anthropic and custom sources

-- Create skills table
CREATE TABLE IF NOT EXISTS skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    content TEXT NOT NULL,  -- Full markdown content
    category VARCHAR(100),
    tags TEXT[],  -- Array of tags for searchability
    source VARCHAR(50) DEFAULT 'anthropic',  -- 'anthropic', 'custom', etc.
    source_url VARCHAR(500),  -- GitHub or reference URL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_skills_skill_id ON skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category);
CREATE INDEX IF NOT EXISTS idx_skills_created_at ON skills(created_at);

-- Create GIN index for tag array searches
CREATE INDEX IF NOT EXISTS idx_skills_tags ON skills USING GIN(tags);

-- Create text search index for title and description
CREATE INDEX IF NOT EXISTS idx_skills_title_description
ON skills USING GIN(to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- Add comment for documentation
COMMENT ON TABLE skills IS 'Stores agent skills/profiles (Context Artifact Type 1) from Anthropic skills repository and custom sources';
COMMENT ON COLUMN skills.skill_id IS 'Unique skill identifier (e.g., doc-coauthoring, webapp-testing)';
COMMENT ON COLUMN skills.content IS 'Full skill markdown content defining agent capabilities';
COMMENT ON COLUMN skills.category IS 'Skill category: documentation, testing, design, development, file-processing, web-development, communication, general';
COMMENT ON COLUMN skills.tags IS 'Searchable tags array for skill discovery';
COMMENT ON COLUMN skills.source IS 'Source system: anthropic (from GitHub), custom (manually added)';
