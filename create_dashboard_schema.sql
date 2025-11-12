-- Minimal stub of Supabase auth schema for local dev
CREATE SCHEMA IF NOT EXISTS auth;

CREATE TABLE IF NOT EXISTS auth.users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), -- requires pgcrypto
  email TEXT UNIQUE
);

-- Ensure pgcrypto or uuid extension exists (choose one approach)
CREATE EXTENSION IF NOT EXISTS pgcrypto;
