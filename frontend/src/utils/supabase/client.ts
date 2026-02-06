import { createBrowserClient } from '@supabase/ssr';
import { env } from '@/lib/env';

/**
 * Creates a Supabase client for browser/client components.
 * Uses default cookie handling via document.cookie.
 * PKCE code verifier is automatically stored in cookies by Supabase.
 */
export function createClient() {
  return createBrowserClient(
    env.NEXT_PUBLIC_SUPABASE_URL, 
    env.NEXT_PUBLIC_SUPABASE_ANON_KEY
  );
}
