-- =====================================================
-- ENHANCED VULNERABILITY SCANNER - SUPABASE SETUP
-- File 1: Extensions and Custom Types
-- =====================================================
-- Run this file FIRST in Supabase SQL Editor
-- This sets up required PostgreSQL extensions and custom ENUM types

-- =====================================================
-- POSTGRESQL EXTENSIONS
-- =====================================================

-- UUID generation functions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Full-text search and trigram matching
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- GIN indexes for JSONB and arrays
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- =====================================================
-- CUSTOM ENUM TYPES (with existence checks)
-- =====================================================

-- User roles and permissions
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM (
        'admin',
        'user',
        'viewer',
        'analyst',
        'manager'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Project visibility levels
DO $$ BEGIN
    CREATE TYPE project_visibility AS ENUM (
        'private',
        'team',
        'organization',
        'public'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Scan execution status
DO $$ BEGIN
    CREATE TYPE scan_status AS ENUM (
        'pending',
        'queued',
        'running',
        'paused',
        'completed',
        'failed',
        'cancelled',
        'timeout'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Types of security scans
DO $$ BEGIN
    CREATE TYPE scan_type AS ENUM (
        'discovery',
        'vulnerability',
        'full',
        'quick',
        'custom',
        'compliance'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Queue status for crawl queue management
DO $$ BEGIN
    CREATE TYPE queue_status AS ENUM (
        'pending',
        'processing',
        'completed',
        'failed',
        'skipped',
        'timeout'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- HTTP methods for requests
DO $$ BEGIN
    CREATE TYPE http_method AS ENUM (
        'GET',
        'POST',
        'PUT',
        'DELETE',
        'PATCH',
        'HEAD',
        'OPTIONS',
        'TRACE'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Vulnerability severity levels
DO $$ BEGIN
    CREATE TYPE severity_level AS ENUM (
        'critical',
        'high',
        'medium',
        'low',
        'info'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Vulnerability categories (OWASP-based)
DO $$ BEGIN
    CREATE TYPE vulnerability_category AS ENUM (
        'injection',
        'broken_auth',
        'sensitive_data',
        'xml_entities',
        'broken_access',
        'security_misconfig',
        'xss',
        'insecure_deserialization',
        'known_vulnerabilities',
        'insufficient_logging',
        'server_side_forgery',
        'crypto_failures'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Vulnerability status for tracking lifecycle
DO $$ BEGIN
    CREATE TYPE vulnerability_status AS ENUM (
        'open',
        'confirmed',
        'in_progress',
        'resolved',
        'closed',
        'false_positive',
        'accepted_risk',
        'duplicate'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Report output formats
DO $$ BEGIN
    CREATE TYPE report_format AS ENUM (
        'pdf',
        'html',
        'json',
        'csv',
        'xml',
        'docx'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Notification types
DO $$ BEGIN
    CREATE TYPE notification_type AS ENUM (
        'scan_completed',
        'scan_failed',
        'vulnerability_found',
        'report_ready',
        'system_alert',
        'user_invited',
        'subscription_expired'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- External integration types
DO $$ BEGIN
    CREATE TYPE integration_type AS ENUM (
        'slack',
        'discord',
        'teams',
        'jira',
        'github',
        'gitlab',
        'webhook',
        'email',
        'sms'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON EXTENSION "uuid-ossp" IS 'UUID generation functions for primary keys';
COMMENT ON EXTENSION "pg_trgm" IS 'Trigram matching for fuzzy text search';
COMMENT ON EXTENSION "btree_gin" IS 'GIN indexes for JSONB and array columns';

COMMENT ON TYPE user_role IS 'User permission levels within the application';
COMMENT ON TYPE project_visibility IS 'Project access control levels';
COMMENT ON TYPE scan_status IS 'Current state of scan execution';
COMMENT ON TYPE scan_type IS 'Different types of security scans available';
COMMENT ON TYPE queue_status IS 'Status of URLs in the crawl queue';
COMMENT ON TYPE http_method IS 'HTTP request methods for crawling';
COMMENT ON TYPE severity_level IS 'Security vulnerability severity classification';
COMMENT ON TYPE vulnerability_category IS 'OWASP-based vulnerability categorization';
COMMENT ON TYPE vulnerability_status IS 'Vulnerability lifecycle status tracking';
COMMENT ON TYPE report_format IS 'Available output formats for scan reports';
COMMENT ON TYPE notification_type IS 'Types of system notifications';
COMMENT ON TYPE integration_type IS 'Supported external integration platforms';

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Uncomment these to verify extensions and types were created successfully:

-- SELECT * FROM pg_extension WHERE extname IN ('uuid-ossp', 'pg_trgm', 'btree_gin');
-- SELECT typname FROM pg_type WHERE typname LIKE '%_role' OR typname LIKE '%_status' OR typname LIKE '%_type';

-- =====================================================
-- NEXT STEPS
-- =====================================================
-- After running this file successfully:
-- 1. Run 02_core_tables.sql for user profiles and authentication
-- 2. Run 03_project_tables.sql for project management
-- 3. Continue with remaining table creation files
-- 4. Apply RLS policies with 08_rls_policies.sql
-- 5. Add performance indexes with 09_indexes.sql