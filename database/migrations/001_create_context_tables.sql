-- Context API Database Schema
-- This creates the main table for storing user context data

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Main context table
CREATE TABLE IF NOT EXISTS user_contexts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    context_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    app_context JSONB DEFAULT '{}',
    conversation_history JSONB DEFAULT '[]',
    user_preferences JSONB DEFAULT '{}',
    device_info JSONB DEFAULT '{}',
    activity_log JSONB DEFAULT '[]',
    location JSONB DEFAULT '{}',
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_contexts_user_id ON user_contexts(user_id);
CREATE INDEX IF NOT EXISTS idx_user_contexts_session_id ON user_contexts(session_id);
CREATE INDEX IF NOT EXISTS idx_user_contexts_timestamp ON user_contexts(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_user_contexts_context_id ON user_contexts(context_id);

-- Analytics table for tracking API usage
CREATE TABLE IF NOT EXISTS context_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    context_id VARCHAR(255) REFERENCES user_contexts(context_id),
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_analytics_context_id ON context_analytics(context_id);
CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON context_analytics(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_created_at ON context_analytics(created_at DESC);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
CREATE TRIGGER update_user_contexts_updated_at
    BEFORE UPDATE ON user_contexts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
