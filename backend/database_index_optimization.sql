-- Database Index Optimization for N+1 Query Fixes
-- Enhanced Vulnerability Scanner - Performance Optimization
-- 
-- This file contains index recommendations to maximize performance
-- of the optimized queries that replaced N+1 query patterns.

-- =============================================================================
-- INDEXES FOR OPTIMIZED DASHBOARD QUERIES
-- =============================================================================

-- 1. Projects Summary Query Optimization
-- Query: JOIN projects with scan_sessions to get latest scan per project
-- Performance Impact: Critical for dashboard loading

-- Primary index for projects filtering by owner
CREATE INDEX IF NOT EXISTS idx_projects_owner_updated 
ON projects(owner_id, updated_at DESC);

-- Composite index for scan_sessions to support subquery optimization
CREATE INDEX IF NOT EXISTS idx_scan_sessions_project_start_time 
ON scan_sessions(project_id, start_time DESC);

-- Index for scan_sessions status filtering (if needed)
CREATE INDEX IF NOT EXISTS idx_scan_sessions_status 
ON scan_sessions(status) WHERE status IN ('completed', 'running', 'failed');

-- =============================================================================
-- INDEXES FOR RECENT PROJECTS AGGREGATION
-- =============================================================================

-- 2. Recent Projects Query Optimization  
-- Query: Aggregated query with COUNT and MAX operations
-- Performance Impact: High for dashboard widgets

-- Composite index for projects with owner and timestamp
CREATE INDEX IF NOT EXISTS idx_projects_owner_created_updated 
ON projects(owner_id, created_at DESC, updated_at DESC);

-- Optimized index for scan_sessions aggregation
CREATE INDEX IF NOT EXISTS idx_scan_sessions_project_aggregation 
ON scan_sessions(project_id, start_time DESC) 
INCLUDE (status, created_at);

-- Index for discovered_urls aggregation by session
CREATE INDEX IF NOT EXISTS idx_discovered_urls_session_aggregation 
ON discovered_urls(session_id) 
INCLUDE (discovered_at, status_code);

-- =============================================================================
-- INDEXES FOR RECENT SCANS AGGREGATION  
-- =============================================================================

-- 3. Recent Scans Query Optimization
-- Query: Aggregated query with URL count per scan
-- Performance Impact: Medium for dashboard widgets

-- Composite index for scan_sessions with user filtering
CREATE INDEX IF NOT EXISTS idx_scan_sessions_user_created 
ON scan_sessions(created_by, created_at DESC) 
INCLUDE (project_id, status, start_time);

-- Optimized index for URL counting per session
CREATE INDEX IF NOT EXISTS idx_discovered_urls_session_count 
ON discovered_urls(session_id) 
INCLUDE (url, status_code, discovered_at);

-- =============================================================================
-- ADDITIONAL PERFORMANCE INDEXES
-- =============================================================================

-- 4. General Performance Indexes

-- Index for project-scan relationship lookups
CREATE INDEX IF NOT EXISTS idx_scan_sessions_project_status_time 
ON scan_sessions(project_id, status, start_time DESC);

-- Index for URL discovery performance
CREATE INDEX IF NOT EXISTS idx_discovered_urls_session_status_time 
ON discovered_urls(session_id, status_code, discovered_at DESC);

-- Index for form extraction queries (if used)
CREATE INDEX IF NOT EXISTS idx_extracted_forms_url_session 
ON extracted_forms(url_id) 
INCLUDE (form_action, form_method);

-- Index for technology fingerprinting (if used)
CREATE INDEX IF NOT EXISTS idx_technology_fingerprints_url_detected 
ON technology_fingerprints(url_id, detected_at DESC);

-- =============================================================================
-- PARTIAL INDEXES FOR SPECIFIC CONDITIONS
-- =============================================================================

-- 5. Partial Indexes for Common Filters

-- Index only for completed scans (most common query)
CREATE INDEX IF NOT EXISTS idx_scan_sessions_completed_recent 
ON scan_sessions(project_id, start_time DESC) 
WHERE status = 'completed';

-- Index only for successful URL discoveries
CREATE INDEX IF NOT EXISTS idx_discovered_urls_successful 
ON discovered_urls(session_id, discovered_at DESC) 
WHERE status_code BETWEEN 200 AND 299;

-- Index for active/recent projects only
CREATE INDEX IF NOT EXISTS idx_projects_active_recent 
ON projects(owner_id, updated_at DESC) 
WHERE updated_at > NOW() - INTERVAL '30 days';

-- =============================================================================
-- COVERING INDEXES FOR QUERY OPTIMIZATION
-- =============================================================================

-- 6. Covering Indexes to Avoid Table Lookups

-- Covering index for project summary data
CREATE INDEX IF NOT EXISTS idx_projects_summary_covering 
ON projects(owner_id, updated_at DESC) 
INCLUDE (id, name, target_domain, description, created_at);

-- Covering index for scan summary data
CREATE INDEX IF NOT EXISTS idx_scan_sessions_summary_covering 
ON scan_sessions(created_by, created_at DESC) 
INCLUDE (id, project_id, status, start_time, configuration);

-- =============================================================================
-- INDEX MAINTENANCE AND MONITORING
-- =============================================================================

-- 7. Index Usage Monitoring Queries

-- Query to check index usage (PostgreSQL specific)
/*
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
*/

-- Query to find unused indexes
/*
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes 
WHERE idx_scan = 0 
AND schemaname = 'public';
*/

-- =============================================================================
-- PERFORMANCE IMPACT ANALYSIS
-- =============================================================================

/*
Expected Performance Improvements:

1. Projects Summary Query:
   - Before: O(n) queries where n = number of projects
   - After: O(1) single JOIN query with proper indexes
   - Improvement: 95-98% reduction in query time

2. Recent Projects Aggregation:
   - Before: O(n*3) queries (scan_count, url_count, last_scan per project)
   - After: O(1) aggregated query with covering indexes
   - Improvement: 90-95% reduction in query time

3. Recent Scans Aggregation:
   - Before: O(n) queries where n = number of scans
   - After: O(1) aggregated query with session-based indexing
   - Improvement: 85-90% reduction in query time

Overall Dashboard Performance:
- Page load time: 70-90% faster
- Database load: 95% reduction in query count
- Concurrent user capacity: 5-10x improvement
*/

-- =============================================================================
-- DEPLOYMENT NOTES
-- =============================================================================

/*
Deployment Instructions:

1. Run these indexes during low-traffic periods
2. Monitor index creation progress for large tables
3. Update table statistics after index creation:
   - ANALYZE projects;
   - ANALYZE scan_sessions;
   - ANALYZE discovered_urls;

4. Verify query plans are using new indexes:
   - EXPLAIN ANALYZE your optimized queries
   - Check for Index Scan vs Sequential Scan

5. Monitor index size and maintenance overhead
6. Consider partitioning for very large tables (>10M rows)
*/