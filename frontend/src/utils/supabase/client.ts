import { createBrowserClient } from '@supabase/ssr';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL ?? 'https://placeholder.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? 'placeholder-anon-key';

/**
 * Creates a Supabase client for browser/client components.
 * Uses default cookie handling via document.cookie.
 * PKCE code verifier is automatically stored in cookies by Supabase.
 */
export function createClient() {
  return createBrowserClient(supabaseUrl, supabaseAnonKey);
}
