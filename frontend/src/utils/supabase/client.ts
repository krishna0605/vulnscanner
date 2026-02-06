import { createBrowserClient } from '@supabase/ssr';
import { env } from '@/lib/env';

export function createClient() {
  return createBrowserClient(
    env.NEXT_PUBLIC_SUPABASE_URL, 
    env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
    {
      cookies: {
        getAll() {
          // Parse document.cookie into array format expected by Supabase
          return document.cookie.split(';').map(cookie => {
            const [name, ...rest] = cookie.trim().split('=');
            return { 
              name: name || '', 
              value: decodeURIComponent(rest.join('=') || '') 
            };
          }).filter(c => c.name);
        },
        setAll(cookies) {
          // Set each cookie with proper options for production OAuth flow
          cookies.forEach(({ name, value, options }) => {
            const parts = [
              `${name}=${encodeURIComponent(value)}`,
              `path=/`,  // Critical: ensure cookie is accessible to /auth/callback
              'SameSite=Lax',  // Allow cookie on navigation (OAuth redirect)
            ];
            
            // Add Secure flag for HTTPS (production)
            if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
              parts.push('Secure');
            }
            
            // Handle max-age from options
            if (options?.maxAge) {
              parts.push(`max-age=${options.maxAge}`);
            }
            
            document.cookie = parts.join('; ');
          });
        },
      },
    }
  );
}
