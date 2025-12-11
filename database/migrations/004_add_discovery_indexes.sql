-- Migration: Add indexes for Context Discovery queries
-- Description: Optimize search performance for repo, ticket, file, and text queries
-- Date: 2024-12-10

-- ============================================
-- JSONB GIN INDEXES FOR CONTEXT DISCOVERY
-- ============================================

-- Index for repoID queries (most common filter)
CREATE INDEX IF NOT EXISTS idx_context_data_repo_id
ON user_contexts ((context_data->>'repoID'));

-- Index for ticketID queries
CREATE INDEX IF NOT EXISTS idx_context_data_ticket_id
ON user_contexts ((context_data->>'ticketID'));

-- Index for contextLevel queries
CREATE INDEX IF NOT EXISTS idx_context_data_context_level
ON user_contexts ((context_data->>'contextLevel'));

-- GIN index for full JSONB text search (files, AI_Client_type arrays)
CREATE INDEX IF NOT EXISTS idx_context_data_gin
ON user_contexts USING GIN (context_data);

-- Index for details field text search
CREATE INDEX IF NOT EXISTS idx_context_data_details
ON user_contexts USING GIN ((context_data->>'details') gin_trgm_ops);

-- Note: The gin_trgm_ops requires pg_trgm extension
-- Enable it if not already enabled:
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================
-- COMPOSITE INDEXES FOR COMMON QUERY PATTERNS
-- ============================================

-- Index for repo + timestamp (common pattern: recent contexts for a repo)
CREATE INDEX IF NOT EXISTS idx_context_repo_timestamp
ON user_contexts ((context_data->>'repoID'), timestamp DESC);

-- Index for ticket + timestamp
CREATE INDEX IF NOT EXISTS idx_context_ticket_timestamp
ON user_contexts ((context_data->>'ticketID'), timestamp DESC);

-- ============================================
-- EXISTING INDEX OPTIMIZATION
-- ============================================

-- Ensure timestamp index exists for sorting
CREATE INDEX IF NOT EXISTS idx_user_contexts_timestamp
ON user_contexts (timestamp DESC);

-- ============================================
-- VERIFY INDEXES
-- ============================================

-- Run this query to see all indexes on user_contexts:
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'user_contexts';

COMMENT ON INDEX idx_context_data_repo_id IS 'Optimizes queries filtering by repoID';
COMMENT ON INDEX idx_context_data_ticket_id IS 'Optimizes queries filtering by ticketID';
COMMENT ON INDEX idx_context_data_context_level IS 'Optimizes queries filtering by contextLevel';
COMMENT ON INDEX idx_context_data_gin IS 'Optimizes JSONB containment and array queries';
COMMENT ON INDEX idx_context_data_details IS 'Optimizes full-text search in details field';
COMMENT ON INDEX idx_context_repo_timestamp IS 'Optimizes recent contexts for a repo';
COMMENT ON INDEX idx_context_ticket_timestamp IS 'Optimizes recent contexts for a ticket';
