# Supabase Setup Guide

This guide sets up Supabase for VulnScanner, including environment variables, database schema, and Row Level Security (RLS) policies.

## 1) Create a Supabase Project
- Sign in at `https://supabase.com` and create a new project.
- In Project Settings → API, copy your `Project URL` and `anon` public key.
- In your frontend `.env` set:
  - `REACT_APP_SUPABASE_URL=<your-project-url>`
  - `REACT_APP_SUPABASE_ANON_KEY=<your-anon-key>`
  - Keep `REACT_APP_API_BASE_URL=http://127.0.0.1:8000` (or your backend URL).

Restart the frontend dev server after updating `.env`.

## 2) Enable Extensions
Run in the SQL editor:

```sql
-- For UUID generation (if needed)
create extension if not exists pgcrypto;
```

## 3) Schema: Users, Projects, Scans, Findings
Use the SQL below to create core tables. The `profiles` table links Supabase `auth.users` to app-specific metadata.

```sql
-- Profiles (one row per Supabase user)
create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  full_name text,
  organization text,
  avatar_url text,
  created_at timestamp with time zone default now()
);

alter table public.profiles enable row level security;

-- Projects
create table if not exists public.projects (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  owner_id uuid not null references auth.users (id) on delete cascade,
  description text,
  created_at timestamp with time zone default now()
);

alter table public.projects enable row level security;

-- Project members (for shared access)
create table if not exists public.project_members (
  project_id uuid not null references public.projects (id) on delete cascade,
  user_id uuid not null references auth.users (id) on delete cascade,
  role text check (role in ('owner','admin','member')) default 'member',
  added_at timestamp with time zone default now(),
  primary key (project_id, user_id)
);

alter table public.project_members enable row level security;

-- Scans
create table if not exists public.scans (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects (id) on delete cascade,
  target text not null,
  status text check (status in ('Queued','Running','Completed','Warnings','Critical Found','Cancelled')) default 'Queued',
  date timestamp with time zone default now(),
  created_by uuid not null references auth.users (id) on delete set null
);

alter table public.scans enable row level security;

-- Findings
create table if not exists public.findings (
  id uuid primary key default gen_random_uuid(),
  scan_id uuid not null references public.scans (id) on delete cascade,
  title text not null,
  severity text check (severity in ('Critical','High','Medium','Low')) not null,
  cve text,
  description text,
  created_at timestamp with time zone default now()
);

alter table public.findings enable row level security;
```

## 4) Row Level Security (RLS) Policies
Policies ensure users only access their own data or shared projects.

```sql
-- Profiles: user can read and update their own profile
create policy if not exists "profiles_select_own"
  on public.profiles for select
  using (id = auth.uid());

create policy if not exists "profiles_update_own"
  on public.profiles for update
  using (id = auth.uid());

-- Projects: owner or member can select
create policy if not exists "projects_owner_member_select"
  on public.projects for select
  using (
    owner_id = auth.uid() or
    exists (
      select 1 from public.project_members pm
      where pm.project_id = projects.id and pm.user_id = auth.uid()
    )
  );

-- Projects: owner can update/delete; anyone can insert with themselves as owner
create policy if not exists "projects_owner_update"
  on public.projects for update using (owner_id = auth.uid());

create policy if not exists "projects_owner_delete"
  on public.projects for delete using (owner_id = auth.uid());

create policy if not exists "projects_insert_owner_self"
  on public.projects for insert with check (owner_id = auth.uid());

-- Project members: user can see memberships they belong to
create policy if not exists "project_members_select_self"
  on public.project_members for select
  using (user_id = auth.uid());

-- Scans: visible to project owner or members
create policy if not exists "scans_owner_member_select"
  on public.scans for select
  using (
    exists (
      select 1 from public.projects p
      where p.id = scans.project_id and (
        p.owner_id = auth.uid() or
        exists (
          select 1 from public.project_members pm
          where pm.project_id = p.id and pm.user_id = auth.uid()
        )
      )
    )
  );

create policy if not exists "scans_insert_by_project_owner_or_member"
  on public.scans for insert
  with check (
    exists (
      select 1 from public.projects p
      where p.id = scans.project_id and (
        p.owner_id = auth.uid() or
        exists (
          select 1 from public.project_members pm
          where pm.project_id = p.id and pm.user_id = auth.uid()
        )
      )
    )
  );

-- Findings: visible to owner or members via scan
create policy if not exists "findings_owner_member_select"
  on public.findings for select
  using (
    exists (
      select 1 from public.scans s
      join public.projects p on p.id = s.project_id
      where s.id = findings.scan_id and (
        p.owner_id = auth.uid() or
        exists (
          select 1 from public.project_members pm
          where pm.project_id = p.id and pm.user_id = auth.uid()
        )
      )
    )
  );
```

## 5) Profile Auto-Creation (Optional)
Create a profile row on first login using a trigger function:

```sql
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, full_name)
  values (new.id, new.raw_user_meta_data->>'full_name');
  return new;
end;
$$ language plpgsql security definer;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
```

## 6) Testing Queries
Run these sanity checks:

```sql
-- See your profile
select * from public.profiles where id = auth.uid();

-- Create a project (as current user)
insert into public.projects (name, owner_id, description)
values ('My First Project', auth.uid(), 'Demo project');

-- Add yourself as member (optional)
insert into public.project_members (project_id, user_id, role)
select id, auth.uid(), 'owner' from public.projects where owner_id = auth.uid();

-- Create a scan
insert into public.scans (project_id, target, status, created_by)
select id, 'example.com', 'Completed', auth.uid() from public.projects where owner_id = auth.uid() limit 1;

-- Insert a finding
insert into public.findings (scan_id, title, severity, cve, description)
select id, 'SQL Injection', 'High', 'CVE-2024-0000', 'Demo finding' from public.scans limit 1;
```

## 7) Hook Up Frontend
- Ensure `.env` has valid Supabase credentials.
- The app now uses Supabase auth (`AuthContext` and `useAuth`) with protected routes.
- Use the registration and login pages to create accounts and sign in.

If you run into policy errors, check the SQL editor for RLS policies and confirm `auth.uid()` resolves (you must be signed in when executing test queries).

This guide explains how to set up and configure Supabase for the VulnScanner project.

## Overview

The VulnScanner project is fully configured to work with Supabase as the primary database. The backend uses PostgreSQL through Supabase, while the frontend includes the Supabase client for authentication and real-time features.

## Current Status ✅

- ✅ Backend configured for Supabase connectivity
- ✅ Frontend Supabase client library installed
- ✅ Authentication hooks and utilities created
- ✅ Database connection tested and verified
- ✅ Environment configuration template provided

## Prerequisites

1. A Supabase account (free tier available)
2. A Supabase project created
3. Node.js and Python environment set up

## Setup Instructions

### 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up or log in to your account
3. Click "New Project"
4. Choose your organization
5. Fill in project details:
   - **Name**: VulnScanner (or your preferred name)
   - **Database Password**: Choose a strong password
   - **Region**: Select the closest region to your users
6. Click "Create new project"

### 2. Get Your Supabase Credentials

Once your project is created, go to **Settings > API** and copy:

- **Project URL** (e.g., `https://your-project.supabase.co`)
- **Anon/Public Key** (starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)
- **Service Role Key** (starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

Also go to **Settings > Database** and copy:
- **Connection String** (URI format)

### 3. Configure Environment Variables

Create a `.env` file in the project root with your Supabase credentials:

```bash
# Copy from .env.example and fill in your values

# Supabase Database Connection (Backend)
SUPABASE_DB_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres?sslmode=require

# Supabase Client Configuration (Frontend)
REACT_APP_SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
REACT_APP_SUPABASE_ANON_KEY=[YOUR-ANON-KEY]

# Backend Configuration
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_ANON_KEY=[YOUR-ANON-KEY]
SUPABASE_SERVICE_ROLE_KEY=[YOUR-SERVICE-ROLE-KEY]

# Application Security
SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_EXP_MINUTES=60

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Optional: Other services
STRIPE_SECRET_KEY=sk_test_...
REDIS_URL=redis://localhost:6379/0
```

### 4. Set Up Database Schema

The project includes database models that need to be created in Supabase. You can either:

#### Option A: Use Supabase Dashboard
1. Go to **Table Editor** in your Supabase dashboard
2. Create tables manually based on the models in `backend/models/`

#### Option B: Use Database Migrations (Recommended)
1. Install the backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Run the database initialization:
   ```bash
   python -c "
   import asyncio
   from db.session import init_db
   asyncio.run(init_db())
   "
   ```

### 5. Test the Connection

Run the connection test to verify everything is working:

```bash
cd backend
python test_supabase_connection.py
```

You should see output like:
```
🚀 Supabase Connection Test
==================================================
✅ .env file found: C:\path\to\your\.env
🔍 Testing Supabase Database Connection
==================================================
Database URL configured: Yes
✅ Basic connection test: PASSED
✅ Database type: PostgreSQL
✅ SSL connection: on
🎉 Database connection test completed successfully!
🎯 Result: Connection test PASSED
```

### 6. Install Frontend Dependencies

The Supabase client library has already been added to `package.json`. Install it:

```bash
cd frontend
npm install
```

## Usage

### Backend Database Operations

The backend automatically uses Supabase when `SUPABASE_DB_URL` is configured:

```python
from db.session import async_session
from models.user import User

async def create_user(email: str, password: str):
    async with async_session() as session:
        user = User(email=email, hashed_password=password)
        session.add(user)
        await session.commit()
        return user
```

### Frontend Authentication

Use the provided authentication hook:

```typescript
import { useAuth } from './hooks/useAuth';

function LoginComponent() {
  const { signIn, user, loading, error } = useAuth();

  const handleLogin = async (email: string, password: string) => {
    const { error } = await signIn(email, password);
    if (error) {
      console.error('Login failed:', error.message);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (user) return <div>Welcome, {user.email}!</div>;

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      const formData = new FormData(e.target);
      handleLogin(formData.get('email'), formData.get('password'));
    }}>
      <input name="email" type="email" placeholder="Email" required />
      <input name="password" type="password" placeholder="Password" required />
      <button type="submit">Sign In</button>
    </form>
  );
}
```

### Direct Supabase Client Usage

For advanced features, use the Supabase client directly:

```typescript
import { supabase, db, storage } from './lib/supabase';

// Database operations
const { data, error } = await db.select('users').eq('email', 'user@example.com');

// Real-time subscriptions
const subscription = db.subscribe('users', (payload) => {
  console.log('User data changed:', payload);
});

// File storage
const { data, error } = await storage.upload('avatars', 'user-avatar.jpg', file);
```

## Security Configuration

### Row Level Security (RLS)

Enable RLS in Supabase for your tables:

1. Go to **Authentication > Policies**
2. Enable RLS for each table
3. Create policies for different user roles

Example policy for users table:
```sql
-- Users can only see their own data
CREATE POLICY "Users can view own data" ON users
FOR SELECT USING (auth.uid() = id);

-- Users can update their own data
CREATE POLICY "Users can update own data" ON users
FOR UPDATE USING (auth.uid() = id);
```

### Environment Security

- Never commit `.env` files to version control
- Use different Supabase projects for development/staging/production
- Rotate your service role keys regularly
- Use the anon key for frontend, service role key for backend admin operations

## Troubleshooting

### Common Issues

1. **Connection timeout**: Check your internet connection and Supabase project status
2. **SSL errors**: Ensure `sslmode=require` is in your database URL
3. **Authentication errors**: Verify your API keys are correct and not expired
4. **CORS errors**: Add your frontend URL to the CORS origins list

### Windows-Specific Issues

If you encounter psycopg event loop errors on Windows, the test script automatically handles this. For your application, ensure you're using the correct event loop policy.

### Debug Mode

Enable debug logging by setting `echo=True` in the database engine configuration:

```python
# In db/session.py
engine = create_async_engine(db_url, echo=True, future=True)  # Add echo=True
```

## Migration from SQLite

The project automatically falls back to SQLite when no Supabase URL is configured. To migrate:

1. Export your SQLite data
2. Set up Supabase as described above
3. Import your data to Supabase
4. Update your `.env` file
5. Restart your application

## Support

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Discord Community](https://discord.supabase.com)
- [Project Issues](https://github.com/your-repo/issues)

---

**Note**: This setup guide assumes you're using the latest version of the VulnScanner project with all Supabase configurations already in place.