-- Migration: Add embedding column for semantic search
-- Using JSONB to store embedding vectors (compatible with all PostgreSQL versions)

ALTER TABLE skills
ADD COLUMN IF NOT EXISTS embedding JSONB DEFAULT NULL;

-- Create index for faster embedding lookups
CREATE INDEX IF NOT EXISTS idx_skills_embedding ON skills USING GIN (embedding);

COMMENT ON COLUMN skills.embedding IS 'Vector embedding for semantic search (1024-dim array from Bedrock Titan)';
