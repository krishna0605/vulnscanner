-- Minimal schema for testing Enhanced Vulnerability Scanner
-- This creates just the essential tables needed for project creation testing

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (simplified for testing)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Projects table (simplified for testing)
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    target_domain VARCHAR(255) NOT NULL,
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Scan sessions table (simplified for testing)
CREATE TABLE IF NOT EXISTS scan_sessions (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending',
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    configuration JSONB DEFAULT '{}'::jsonb,
    stats JSONB DEFAULT '{}'::jsonb,
    created_by INTEGER REFERENCES users(id)
);

-- Insert a test user for development
INSERT INTO users (id, email, full_name, role, is_active) 
VALUES (1, 'test@example.com', 'Test User', 'user', true)
ON CONFLICT (email) DO NOTHING;

-- Update the sequence to start from 2 (since we inserted ID 1)
SELECT setval('users_id_seq', GREATEST(1, (SELECT MAX(id) FROM users)));

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_projects_owner ON projects(owner_id);
CREATE INDEX IF NOT EXISTS idx_scan_sessions_project ON scan_sessions(project_id);

-- Simple RLS policies (optional for testing)
-- ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Users can view their own projects" ON projects FOR SELECT USING (owner_id = 1);
-- CREATE POLICY "Users can create their own projects" ON projects FOR INSERT WITH CHECK (owner_id = 1);