import { createClient } from '@supabase/supabase-js';
import { env } from './env';

/**
 * Supabase client initialized with validated environment variables.
 * Uses the service role key for backend operations (bypasses RLS).
 */
export const supabase = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY);
