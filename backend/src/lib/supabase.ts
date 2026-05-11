import { createClient } from '@supabase/supabase-js';
import { env } from './env';

const supabaseUrl = env.SUPABASE_URL ?? 'https://placeholder.supabase.co';
const supabaseServiceKey = env.SUPABASE_SERVICE_ROLE_KEY ?? 'placeholder-service-role-key';

/**
 * Transitional Supabase client for legacy routes retained during migration/backout.
 * Scanner endpoints use Convex; legacy endpoints require real Supabase env vars.
 */
export const supabase = createClient(supabaseUrl, supabaseServiceKey);
