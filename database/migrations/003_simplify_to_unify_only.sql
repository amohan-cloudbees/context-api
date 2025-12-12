-- Migration: Simplify schema to focus on Unify workflow context only
-- Date: 2024-12-09

-- Drop context_type enum and related columns (no longer needed)
ALTER TABLE user_contexts DROP COLUMN IF EXISTS context_type;
ALTER TABLE user_contexts DROP COLUMN IF EXISTS slack_data;
ALTER TABLE user_contexts DROP COLUMN IF EXISTS unify_data;
ALTER TABLE user_contexts DROP COLUMN IF EXISTS app_context;
ALTER TABLE user_contexts DROP COLUMN IF EXISTS conversation_history;
ALTER TABLE user_contexts DROP COLUMN IF EXISTS user_preferences;
ALTER TABLE user_contexts DROP COLUMN IF EXISTS device_info;
ALTER TABLE user_contexts DROP COLUMN IF EXISTS activity_log;
ALTER TABLE user_contexts DROP COLUMN IF EXISTS location;

-- Add single unified context_data column
ALTER TABLE user_contexts ADD COLUMN IF NOT EXISTS context_data JSONB NOT NULL DEFAULT '{}';

-- Drop old indexes
DROP INDEX IF EXISTS idx_user_contexts_context_type;
DROP INDEX IF EXISTS idx_slack_data_gin;
DROP INDEX IF EXISTS idx_unify_data_gin;

-- Create new index on context_data
CREATE INDEX IF NOT EXISTS idx_context_data_gin ON user_contexts USING GIN (context_data);

-- Drop context_type_enum
DROP TYPE IF EXISTS context_type_enum;

-- Add comment
COMMENT ON COLUMN user_contexts.context_data IS 'Workflow context data (repoID, ticketID, catalogID, files, etc.)';
