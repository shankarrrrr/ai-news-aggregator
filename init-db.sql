-- Initialize database for AI-Powered Competitive Exam Intelligence System
-- This script runs automatically when the PostgreSQL container starts

-- Create database if it doesn't exist (handled by POSTGRES_DB env var)
-- CREATE DATABASE IF NOT EXISTS ai_news_aggregator;

-- Set timezone
SET timezone = 'UTC';

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE ai_news_aggregator TO postgres;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialized for AI-Powered Competitive Exam Intelligence System';
    RAISE NOTICE 'Timestamp: %', NOW();
END $$;