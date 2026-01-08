-- =============================================================================
-- AI DATA ANALYST - DATABASE SCHEMA (PostgreSQL)
-- =============================================================================
-- Run this in Neon PostgreSQL console or via migration script
-- =============================================================================

-- Enable UUID extension for generating unique table names
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- USERS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster email lookups (login)
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- =============================================================================
-- DATASETS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS datasets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    table_name VARCHAR(255) NOT NULL,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    schema_info TEXT, -- JSON containing column info, quality report, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for user dataset queries
CREATE INDEX IF NOT EXISTS idx_datasets_owner_id ON datasets(owner_id);

-- Index for table name lookups
CREATE INDEX IF NOT EXISTS idx_datasets_table_name ON datasets(table_name);

-- =============================================================================
-- CHAT HISTORY TABLE (Optional - for conversation context)
-- =============================================================================
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dataset_id INTEGER REFERENCES datasets(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    title VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);

-- =============================================================================
-- RAG INDEX TRACKING TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS rag_indices (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    index_type VARCHAR(50) DEFAULT 'hybrid',
    document_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rag_indices_user_id ON rag_indices(user_id);

-- =============================================================================
-- DATABASE FUNCTIONS
-- =============================================================================

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for users table
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for datasets table
DROP TRIGGER IF EXISTS update_datasets_updated_at ON datasets;
CREATE TRIGGER update_datasets_updated_at
    BEFORE UPDATE ON datasets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for rag_indices table
DROP TRIGGER IF EXISTS update_rag_indices_updated_at ON rag_indices;
CREATE TRIGGER update_rag_indices_updated_at
    BEFORE UPDATE ON rag_indices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================
COMMENT ON TABLE users IS 'Registered users of the AI Data Analyst platform';
COMMENT ON TABLE datasets IS 'Uploaded CSV datasets with metadata and schema information';
COMMENT ON TABLE chat_sessions IS 'Chat conversation sessions for tracking conversation history';
COMMENT ON TABLE rag_indices IS 'RAG (Retrieval-Augmented Generation) index metadata for hybrid search';

-- =============================================================================
-- SAMPLE DATA (Optional - for testing)
-- =============================================================================
-- INSERT INTO users (email, hashed_password) VALUES 
-- ('test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4oQyHN4y6tJE9Edy'); -- password: test123

