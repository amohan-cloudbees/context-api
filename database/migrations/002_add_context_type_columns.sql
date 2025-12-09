-- Migration: Add context_type and separate data columns for Slack and Unify contexts
-- Date: 2024-12-09

-- Add context_type column with enum
DO $$ BEGIN
    CREATE TYPE context_type_enum AS ENUM ('slack', 'unify');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Add new columns to user_contexts table
ALTER TABLE user_contexts
ADD COLUMN IF NOT EXISTS context_type context_type_enum DEFAULT 'slack',
ADD COLUMN IF NOT EXISTS slack_data JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS unify_data JSONB DEFAULT '{}';

-- Migrate existing data to slack_data (backward compatibility)
UPDATE user_contexts
SET
    context_type = 'slack',
    slack_data = jsonb_build_object(
        'appContext', app_context,
        'conversationHistory', conversation_history,
        'userPreferences', user_preferences,
        'deviceInfo', device_info,
        'activityLog', activity_log,
        'location', location
    )
WHERE context_type IS NULL OR slack_data = '{}';

-- Create index on context_type for faster queries
CREATE INDEX IF NOT EXISTS idx_user_contexts_context_type ON user_contexts(context_type);

-- Create index on slack_data JSONB fields (for common queries)
CREATE INDEX IF NOT EXISTS idx_slack_data_gin ON user_contexts USING GIN (slack_data);

-- Create index on unify_data JSONB fields (for common queries)
CREATE INDEX IF NOT EXISTS idx_unify_data_gin ON user_contexts USING GIN (unify_data);

-- Add comments
COMMENT ON COLUMN user_contexts.context_type IS 'Type of context: slack (conversational) or unify (workflow)';
COMMENT ON COLUMN user_contexts.slack_data IS 'Slack-specific context data (conversationHistory, preferences, etc.)';
COMMENT ON COLUMN user_contexts.unify_data IS 'Unify-specific context data (repoID, ticketID, catalogID, etc.)';
