import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';
import { env } from '@/lib/env';

/**
 * Creates a Supabase client for Server Components.
 * Uses the newer getAll/setAll cookie pattern for consistency.
 * @param persistSession - When true, sets cookie maxAge to 30 days for "Remember Me"
 */
export function createClient(persistSession = false) {
  const cookieStore = cookies();
  // 30 days for "Remember Me", otherwise use session cookie (no maxAge)
  const maxAge = persistSession ? 60 * 60 * 24 * 30 : undefined;

  return createServerClient(env.NEXT_PUBLIC_SUPABASE_URL, env.NEXT_PUBLIC_SUPABASE_ANON_KEY, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet) {
        try {
          cookiesToSet.forEach(({ name, value, options }) => {
            const cookieOptions = persistSession 
              ? { ...options, maxAge, sameSite: 'lax' as const }
              : options;
            cookieStore.set(name, value, cookieOptions);
          });
        } catch {
          // The `setAll` method was called from a Server Component.
          // This can be ignored if you have middleware refreshing
          // user sessions.
        }
      },
    },
  });
}
