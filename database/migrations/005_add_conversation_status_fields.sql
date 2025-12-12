-- Migration: Add indexes for conversationHistory and status fields
-- Date: 2024-12-11
-- Description: Optimize queries filtering by workflow status

-- Add GIN index on status field for fast filtering
CREATE INDEX IF NOT EXISTS idx_context_data_status
ON user_contexts ((context_data->>'status'));

-- Add comment explaining the fields
COMMENT ON COLUMN user_contexts.context_data IS 'Workflow context data including conversationHistory, status, blockedBy, repoID, ticketID, files, etc.';

-- Index usage examples:
-- SELECT * FROM user_contexts WHERE context_data->>'status' = 'blocked';
-- SELECT * FROM user_contexts WHERE context_data->>'status' = 'in_progress';
