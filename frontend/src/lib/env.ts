import { z } from 'zod';

/**
 * Client-side environment schema (only NEXT_PUBLIC_ vars accessible in browser)
 */
const clientEnvSchema = z.object({
  NEXT_PUBLIC_SUPABASE_URL: z.string().url('NEXT_PUBLIC_SUPABASE_URL must be a valid URL'),
  NEXT_PUBLIC_SUPABASE_ANON_KEY: z.string().min(1, 'NEXT_PUBLIC_SUPABASE_ANON_KEY is required'),
  NEXT_PUBLIC_SENTRY_DSN: z.string().url().optional(),
});

/**
 * Server-side environment schema (all vars, only available on server)
 */
const serverEnvSchema = clientEnvSchema.extend({
  BACKEND_URL: z
    .string()
    .transform((val) => {
      if (!val) return 'http://localhost:3001';
      if (val.startsWith('http')) return val;
      return `https://${val}`;
    })
    .pipe(z.string().url())
    .optional()
    .default('http://localhost:3001'),
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
});

export type ClientEnv = z.infer<typeof clientEnvSchema>;
export type ServerEnv = z.infer<typeof serverEnvSchema>;

/**
 * Creates validated environment object based on runtime context.
 * Uses different schemas for client vs server.
 */
function createEnv(): ServerEnv {
  const isServer = typeof window === 'undefined';

  // Build env object from process.env
  const envVars: Record<string, string | undefined> = {
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
    NEXT_PUBLIC_SENTRY_DSN: process.env.NEXT_PUBLIC_SENTRY_DSN,
  };

  // Add server-only vars if on server
  if (isServer) {
    envVars.BACKEND_URL = process.env.BACKEND_URL;
    envVars.NODE_ENV = process.env.NODE_ENV;
  }

  const schema = isServer ? serverEnvSchema : clientEnvSchema;
  const result = schema.safeParse(envVars);

  if (!result.success) {
    const errorMessages = result.error.issues
      .map((issue) => `  • ${issue.path.join('.')}: ${issue.message}`)
      .join('\n');

    console.error('\n❌ Invalid environment variables:\n');
    console.error(errorMessages);
    console.error('\nPlease check your .env.local file or environment configuration.\n');

    // In development, throw to fail fast
    // In production/build, we want the error to be visible
    throw new Error(`Invalid environment configuration:\n${errorMessages}`);
  }

  return result.data as ServerEnv;
}

/**
 * Validated and typed environment variables.
 * Import this instead of using process.env directly.
 *
 * @example
 * import { env } from '@/lib/env';
 * const supabase = createClient(env.NEXT_PUBLIC_SUPABASE_URL, env.NEXT_PUBLIC_SUPABASE_ANON_KEY);
 */
export const env = createEnv();

/**
 * Helper to check if we're in production mode.
 */
export const isProduction = env.NODE_ENV === 'production';

/**
 * Helper to check if we're in development mode.
 */
export const isDevelopment = env.NODE_ENV === 'development';
