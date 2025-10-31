# Combined Schema Usage Guide

## Overview
The `combined_schema.sql` file contains the complete database schema for the Enhanced Vulnerability Scanner, combining all individual SQL files into a single executable script.

## Execution Order
The combined file follows this execution order:
1. **Extensions & Types** - PostgreSQL extensions and custom ENUM types
2. **Core Tables** - User management, billing, and system tables
3. **Project Tables** - Project management and collaboration
4. **Scanning Tables** - Scan execution and URL discovery
5. **Vulnerability Tables** - Security findings and analysis
6. **Reporting Tables** - Reports, analytics, and metrics
7. **Integration Tables** - Notifications, webhooks, and external APIs
8. **Row Level Security (RLS)** - Security policies and helper functions
9. **Performance Indexes** - Database optimization indexes
10. **Views & Materialized Views** - Data aggregation views
11. **Security Fixes** - Additional constraints and verification

## How to Use

### Option 1: Initial Deployment - Pure Clean (Recommended for Fresh Databases)
```sql
-- Use the pure clean version for initial deployment - NO destructive operation warnings
-- Copy and paste combined_schema_initial.sql content into Supabase SQL Editor
-- This version removes ALL DROP statements for completely clean deployment
```

### Option 2: Initial Deployment - Standard Clean (Alternative)
```sql
-- Use the standard clean version for initial deployment
-- Copy and paste combined_schema_clean.sql content into Supabase SQL Editor
-- This version removes DROP TRIGGER statements but may still show warnings
```

### Option 3: Updates/Re-deployments
```sql
-- Use the full version for updates or re-deployments
-- Copy and paste combined_schema.sql content into Supabase SQL Editor
-- This version includes DROP statements for safe re-execution
```

### Option 3: Individual File Execution
```bash
# Execute files in order (if needed for debugging)
psql -f 01_extensions_and_types.sql
psql -f 02_core_tables.sql
psql -f 03_project_tables.sql
psql -f 04_scanning_tables.sql
psql -f 05_vulnerability_tables.sql
psql -f 06_reporting_tables.sql
psql -f 07_integration_tables.sql
psql -f 08_rls_policies.sql
psql -f 09_indexes_constraints.sql
psql -f 10_security_fixes.sql
```

### Option 4: Command Line (psql)
```bash
psql -h your-supabase-host -p 5432 -U postgres -d postgres -f combined_schema.sql
```

### Option 5: Supabase CLI
```bash
supabase db reset
# Then apply the schema
supabase db push
```

## Important Notes

### Prerequisites
- Supabase project with PostgreSQL 15+
- Required extensions: `uuid-ossp`, `pg_trgm`, `btree_gin`
- Supabase Auth enabled

### Execution Guidelines
- **Execution Order**: The combined file maintains the correct execution order automatically
- **Idempotent**: Safe to run multiple times (uses IF NOT EXISTS, IF EXISTS patterns)
- **RLS Enabled**: All tables have Row Level Security enabled with appropriate policies
- **Performance**: Includes optimized indexes for common query patterns
- **Security**: Implements OWASP best practices and secure defaults

## Handling Destructive Operations

### Supabase Warning: "Query has destructive operation"
If you encounter this warning, it's due to `DROP TRIGGER IF EXISTS` statements that ensure safe re-execution.

**For Initial Deployment:**
- Use `combined_schema_clean.sql` - removes all DROP statements
- No destructive operation warnings
- Safe for fresh database setup

**For Updates/Re-deployments:**
- Use `combined_schema.sql` - includes DROP statements for safety
- Click "Run this query" to proceed (the operations are safe)
- Ensures triggers are recreated properly

### File Comparison:
- `combined_schema.sql`: Full version with DROP statements (100,547 bytes)
- `combined_schema_clean.sql`: Clean version with conditional triggers (102,082 bytes)  
- `combined_schema_initial.sql`: Pure clean version with NO DROP statements (42,606 bytes)
- **Recommended**: Use `combined_schema_initial.sql` for initial deployments to completely avoid warnings

### Trigger Conflict Resolution
If you encounter `ERROR: 42710: trigger "trigger_name" for relation "table_name" already exists`:

**Root Cause**: Supabase environments may have pre-existing triggers that conflict with schema deployment.

**Solution**: Both schema versions now include `DROP TRIGGER IF EXISTS` statements:
- `combined_schema_clean.sql`: Updated to handle existing triggers gracefully
- Safe for both fresh deployments and environments with existing triggers
- No more "trigger already exists" errors

**Auto-Fix Script**: Use `fix_clean_triggers.py` to update clean schema with conditional trigger creation.

## Version History

### v1.5 (Latest)
- **Fix**: Resolved trigger conflicts in `combined_schema_clean.sql`
- **Change**: Added `DROP TRIGGER IF EXISTS` to clean schema for existing trigger handling
- **Impact**: Clean schema now safe for environments with pre-existing triggers
- **Files**: `combined_schema_clean.sql`, `fix_clean_triggers.py`
- **Error Fixed**: `ERROR: 42710: trigger "trigger_name" for relation "table_name" already exists`

### v1.6
- **Fix**: Completely eliminated Supabase "Query has destructive operation" warnings
- **Change**: Created `combined_schema_initial.sql` with NO DROP statements
- **Impact**: Removed ALL 31 DROP statements for pure clean deployment
- **Files**: `combined_schema_initial.sql`, `create_pure_clean_schema.py`
- **Usage**: Use initial version for fresh deployments, clean/full versions for updates

### v1.5
- **Fix**: Resolved trigger conflicts in clean schema
- **Change**: Added `DROP TRIGGER IF EXISTS` statements to `combined_schema_clean.sql`
- **Impact**: Made clean schema safe for environments with pre-existing triggers
- **Files**: `combined_schema_clean.sql`, `fix_clean_triggers.py`
- **Error Fixed**: `ERROR: 42710: trigger "trigger_name" for relation "table_name" already exists`

### v1.4
- **Fix**: Resolved Supabase "Query has destructive operation" warning
- **Change**: Created `combined_schema_clean.sql` for initial deployments
- **Impact**: Removed 31 DROP TRIGGER statements from clean version
- **Files**: `combined_schema_clean.sql`, `create_clean_schema.py`
- **Usage**: Use clean version for fresh deployments, full version for updates

### v1.3
- **Fix**: Resolved "trigger already exists" errors
- **Change**: Added `DROP TRIGGER IF EXISTS` before `CREATE TRIGGER` statements
- **Impact**: 31 trigger statements modified for safe re-execution
- **Files**: `combined_schema.sql`, `fix_triggers.py`

### v1.2
- Fixed "type already exists" errors by wrapping all `CREATE TYPE` statements with exception handling
- Allows safe re-execution of schema on databases where types might already exist
- Uses `DO $$ BEGIN ... EXCEPTION WHEN duplicate_object THEN null; END $$;` pattern for all custom types

### v1.1
- Fixed PostgreSQL reserved keyword conflict: renamed `references` column to `reference_links` in `vulnerability_types` table
- Maintains full backward compatibility with existing data

### Recent Changes
- **v1.3**: Added `DROP TRIGGER IF EXISTS` statements to prevent "trigger already exists" errors
- **v1.2**: Added exception handling for CREATE TYPE statements to prevent "type already exists" errors

### Security Features
- Row Level Security (RLS) enabled on all tables
- Helper functions for access control
- Comprehensive security policies
- Data isolation by project membership

### Performance Optimizations
- Composite indexes for complex queries
- Partial indexes for filtered data
- GIN indexes for JSONB columns
- Text search indexes for full-text search

### Verification
After execution, run these verification queries:

```sql
-- Check RLS is enabled
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND rowsecurity = false;

-- Verify policies exist
SELECT COUNT(*) as policy_count
FROM pg_policies 
WHERE schemaname = 'public';

-- Check helper functions
SELECT routine_name 
FROM information_schema.routines 
WHERE routine_schema = 'public' 
AND routine_name LIKE '%project%' OR routine_name LIKE '%admin%';
```

## Rollback
If you need to rollback:
1. Drop all tables: `DROP SCHEMA public CASCADE; CREATE SCHEMA public;`
2. Or use Supabase dashboard to reset the database

## Support
- Check the original individual SQL files for detailed comments
- Refer to the project documentation for schema explanations
- Use the verification queries to ensure proper setup