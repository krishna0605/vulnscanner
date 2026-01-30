import { z } from 'zod';
import dotenv from 'dotenv';
import path from 'path';

// Load environment variables from .env file
dotenv.config({ path: path.resolve(__dirname, '../../.env') });

/**
 * Environment variable schema for the backend application.
 * All environment variables are validated at startup using Zod.
 * If any required variable is missing or invalid, the app will fail to start.
 */
const envSchema = z.object({
  // Database
  SUPABASE_URL: z.string().url('SUPABASE_URL must be a valid URL'),
  SUPABASE_SERVICE_ROLE_KEY: z.string().min(1, 'SUPABASE_SERVICE_ROLE_KEY is required'),
  DATABASE_URL: z.string().url().optional(),

  // Server
  PORT: z.coerce.number().default(3001),
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  LOG_LEVEL: z.enum(['fatal', 'error', 'warn', 'info', 'debug', 'trace']).default('info'),

  // Security
  ALLOWED_ORIGINS: z.string().optional(),
  RATE_LIMIT_MAX: z.coerce.number().default(100),
  RATE_LIMIT_WINDOW_MS: z.coerce.number().default(60000),

  // Monitoring
  SENTRY_DSN: z.string().url().optional(),
});

export type Env = z.infer<typeof envSchema>;

/**
 * Validates environment variables against the schema.
 * Exits the process with detailed error messages if validation fails.
 */
function validateEnv(): Env {
  const result = envSchema.safeParse(process.env);

  if (!result.success) {
    console.error('');
    console.error('❌ Invalid environment variables:');
    console.error('');
    result.error.issues.forEach((issue) => {
      console.error(`   • ${issue.path.join('.')}: ${issue.message}`);
    });
    console.error('');
    console.error('Please check your .env file or environment configuration.');
    console.error('');
    process.exit(1);
  }

  return result.data;
}

/**
 * Validated and typed environment variables.
 * Import this instead of using process.env directly.
 */
export const env = validateEnv();

/**
 * Helper to check if we're in production mode.
 */
export const isProduction = env.NODE_ENV === 'production';

/**
 * Helper to check if we're in development mode.
 */
export const isDevelopment = env.NODE_ENV === 'development';

/**
 * Helper to check if we're in test mode.
 */
export const isTest = env.NODE_ENV === 'test';
