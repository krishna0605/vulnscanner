# Enhanced Vulnerability Scanner - Supabase Database Setup

This directory contains SQL files to set up the complete database schema for the Enhanced Vulnerability Scanner in Supabase. The files are organized in a specific execution order to ensure proper dependencies and relationships.

## 📋 Overview

The database schema has been converted from the original `DATABASE_SCHEMA_DESIGN.sql` into 9 organized SQL files that can be executed sequentially in the Supabase SQL Editor.

## 🗂️ File Structure

```
supabase_sql/
├── 01_extensions_and_types.sql    # PostgreSQL extensions and custom ENUM types
├── 02_core_tables.sql             # User profiles, API keys, authentication
├── 03_project_tables.sql          # Project management and collaboration
├── 04_scanning_tables.sql         # Scan sessions, crawling, URL discovery
├── 05_vulnerability_tables.sql    # Vulnerability management and security analysis
├── 06_reporting_tables.sql        # Reports, analytics, dashboard metrics
├── 07_integration_tables.sql      # Notifications, webhooks, integrations
├── 08_rls_policies.sql            # Row Level Security policies
├── 09_indexes.sql                 # Performance indexes and constraints
└── README.md                      # This file
```

## 🚀 Execution Instructions

### Prerequisites

1. **Supabase Project**: Ensure you have a Supabase project created
2. **Database Access**: Access to the Supabase SQL Editor
3. **Permissions**: Admin/Owner permissions on the Supabase project

### Step-by-Step Execution

Execute the SQL files in the **exact order** listed below. Each file builds upon the previous ones:

#### 1. Extensions and Types
```sql
-- File: 01_extensions_and_types.sql
-- Purpose: Set up PostgreSQL extensions and custom ENUM types
-- Dependencies: None
```
- Enables `uuid-ossp`, `pg_trgm`, and `btree_gin` extensions
- Creates custom ENUM types for user roles, scan statuses, severity levels, etc.

#### 2. Core Tables
```sql
-- File: 02_core_tables.sql
-- Purpose: User management, authentication, and system tables
-- Dependencies: 01_extensions_and_types.sql
```
- Creates user profiles, API keys, sessions
- Sets up subscriptions, usage tracking
- Establishes system settings and background jobs

#### 3. Project Tables
```sql
-- File: 03_project_tables.sql
-- Purpose: Project management and collaboration features
-- Dependencies: 01, 02
```
- Creates projects, members, settings
- Sets up invitations, comments, favorites
- Establishes project activity tracking

#### 4. Scanning Tables
```sql
-- File: 04_scanning_tables.sql
-- Purpose: Scan execution, crawling, and URL discovery
-- Dependencies: 01, 02, 03
```
- Creates scan sessions, crawl queue
- Sets up URL discovery and metadata
- Establishes form extraction and technology fingerprinting

#### 5. Vulnerability Tables
```sql
-- File: 05_vulnerability_tables.sql
-- Purpose: Vulnerability management and security analysis
-- Dependencies: 01, 02, 03, 04
```
- Creates vulnerability types and instances
- Sets up SSL certificate and DNS analysis
- Establishes compliance frameworks

#### 6. Reporting Tables
```sql
-- File: 06_reporting_tables.sql
-- Purpose: Reports, analytics, and dashboard metrics
-- Dependencies: 01, 02, 03, 04, 05
```
- Creates scan reports and schedules
- Sets up analytics events and metrics
- Establishes export jobs and templates

#### 7. Integration Tables
```sql
-- File: 07_integration_tables.sql
-- Purpose: Notifications, webhooks, and external integrations
-- Dependencies: 01, 02, 03, 04, 05, 06
```
- Creates notifications and preferences
- Sets up webhooks and external APIs
- Establishes integration logging

#### 8. RLS Policies
```sql
-- File: 08_rls_policies.sql
-- Purpose: Row Level Security for data access control
-- Dependencies: All previous files (01-07)
```
- Enables RLS on all tables
- Creates helper functions for access control
- Establishes comprehensive security policies

#### 9. Performance Indexes
```sql
-- File: 09_indexes.sql
-- Purpose: Optimize query performance and add constraints
-- Dependencies: All previous files (01-08)
```
- Creates performance indexes for all tables
- Adds unique constraints and check constraints
- Sets up composite and partial indexes

## 🔧 Execution Methods

### Method 1: Supabase SQL Editor (Recommended)

1. Open your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Create a new query for each file
4. Copy and paste the content of each SQL file
5. Execute them **in order** (01 → 02 → 03 → ... → 09)

### Method 2: Supabase CLI

```bash
# If you have Supabase CLI installed
supabase db reset
supabase db push

# Or execute individual files
supabase db execute --file 01_extensions_and_types.sql
supabase db execute --file 02_core_tables.sql
# ... continue for all files
```

### Method 3: psql (Direct Connection)

```bash
# Connect to your Supabase database
psql "postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres"

# Execute files in order
\i 01_extensions_and_types.sql
\i 02_core_tables.sql
\i 03_project_tables.sql
\i 04_scanning_tables.sql
\i 05_vulnerability_tables.sql
\i 06_reporting_tables.sql
\i 07_integration_tables.sql
\i 08_rls_policies.sql
\i 09_indexes.sql
```

## ✅ Verification

After executing all files, run these verification queries in the SQL Editor:

### Check Tables Created
```sql
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

### Check RLS Policies
```sql
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE schemaname = 'public' 
ORDER BY tablename, policyname;
```

### Check Indexes
```sql
SELECT schemaname, tablename, indexname, indexdef 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;
```

### Check Functions
```sql
SELECT routine_name, routine_type, data_type 
FROM information_schema.routines 
WHERE routine_schema = 'public' 
ORDER BY routine_name;
```

## 🔍 Key Features

### Security Features
- **Row Level Security (RLS)**: Enabled on all tables with comprehensive policies
- **User Authentication**: Integration with Supabase Auth
- **API Key Management**: Secure API key storage and validation
- **Role-Based Access**: Project-level permissions and user roles

### Performance Optimizations
- **Comprehensive Indexing**: Optimized indexes for all query patterns
- **Materialized Views**: Pre-computed analytics and summaries
- **Partial Indexes**: Efficient indexes for filtered queries
- **GIN Indexes**: Full-text search and JSONB column optimization

### Data Integrity
- **Foreign Key Constraints**: Proper relationships between tables
- **Check Constraints**: Data validation at database level
- **Unique Constraints**: Prevent duplicate data
- **Triggers**: Automatic timestamp updates and data consistency

## 📊 Database Schema Overview

### Core Entities
- **Users & Authentication**: Profiles, API keys, sessions
- **Projects**: Project management, members, settings
- **Scans**: Scan sessions, configurations, scheduling
- **URLs**: Discovery, metadata, forms, technologies
- **Vulnerabilities**: Types, instances, analysis, compliance
- **Reports**: Generation, scheduling, analytics
- **Integrations**: Notifications, webhooks, external APIs

### Key Relationships
- Users own and collaborate on Projects
- Projects contain multiple Scan Sessions
- Scans discover URLs and identify Vulnerabilities
- Vulnerabilities generate Reports and Notifications
- Integrations connect to external systems

## 🚨 Important Notes

### Execution Order
- **CRITICAL**: Execute files in the exact order specified (01-09)
- Each file depends on the previous ones
- Skipping files or changing order will cause errors

### Supabase Considerations
- Some features may require Supabase Pro plan (e.g., custom domains)
- RLS policies work with Supabase Auth automatically
- Materialized views need manual refresh or scheduled jobs

### Performance
- Initial setup may take 5-10 minutes for all files
- Index creation is the longest step (file 09)
- Monitor database size and performance after setup

## 🔧 Troubleshooting

### Common Issues

1. **Extension Not Available**
   ```sql
   -- If pg_trgm or btree_gin extensions fail
   -- Contact Supabase support or use alternative indexes
   ```

2. **Permission Errors**
   ```sql
   -- Ensure you have admin/owner access to the project
   -- Check if RLS is interfering with operations
   ```

3. **Constraint Violations**
   ```sql
   -- Check for existing data that conflicts with new constraints
   -- Clean up data before applying constraints
   ```

### Recovery Steps

If execution fails midway:

1. **Identify the failing file/statement**
2. **Check error message for specific issue**
3. **Fix the issue (permissions, data conflicts, etc.)**
4. **Continue from the failed file**
5. **Do not re-run successfully executed files**

## 📈 Next Steps

After successful database setup:

1. **Configure Supabase Auth**: Set up authentication providers
2. **Set Environment Variables**: Update your application config
3. **Test Connections**: Verify database connectivity from your app
4. **Seed Initial Data**: Add default vulnerability types and settings
5. **Set up Monitoring**: Configure logging and performance monitoring

## 🤝 Support

If you encounter issues:

1. Check the verification queries above
2. Review Supabase logs in the dashboard
3. Consult the original `DATABASE_SCHEMA_DESIGN.sql` for reference
4. Check Supabase documentation for specific features

---

**Total Tables Created**: ~40 tables
**Total Indexes Created**: ~150+ indexes
**Total RLS Policies**: ~80+ policies
**Estimated Setup Time**: 5-10 minutes

Good luck with your Enhanced Vulnerability Scanner setup! 🚀