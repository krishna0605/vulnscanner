import { FastifyRequest, FastifyReply, FastifyInstance } from 'fastify';
import { createClient } from '@supabase/supabase-js';

// User payload attached to request after authentication
export interface AuthUser {
  id: string;
  email?: string;
  role?: string;
}

// Extend FastifyRequest to include user
declare module 'fastify' {
  interface FastifyRequest {
    user?: AuthUser;
  }
}

// Initialize Supabase client for token verification
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseServiceKey) {
  console.warn('[Auth] Legacy Supabase auth is disabled because Supabase env vars are missing.');
}

const supabase = supabaseUrl && supabaseServiceKey 
  ? createClient(supabaseUrl, supabaseServiceKey)
  : null;

/**
 * Legacy JWT Authentication Middleware.
 * Scanner endpoints use SCANNER_SERVICE_TOKEN and Convex HTTP actions.
 */
export async function authenticateRequest(
  request: FastifyRequest,
  reply: FastifyReply
): Promise<void> {
  const authHeader = request.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    reply.status(401).send({
      statusCode: 401,
      error: 'Unauthorized',
      message: 'Missing or invalid Authorization header. Use: Bearer <token>',
    });
    return;
  }

  const token = authHeader.substring(7); // Remove 'Bearer ' prefix

  try {
    // Check if Supabase is properly configured
    if (!supabase) {
      console.error('[Auth] Supabase client not initialized - missing env vars');
      reply.status(500).send({
        statusCode: 500,
        error: 'Server Configuration Error',
        message: 'Authentication service not properly configured',
      });
      return;
    }

    // Verify the token with Supabase
    const {
      data: { user },
      error,
    } = await supabase.auth.getUser(token);

    if (error || !user) {
      reply.status(401).send({
        statusCode: 401,
        error: 'Unauthorized',
        message: 'Invalid or expired token',
      });
      return;
    }

    // Attach user to request for use in route handlers
    request.user = {
      id: user.id,
      email: user.email,
      role: user.role,
    };
  } catch (err) {
    request.log.error({ err }, 'Token verification failed');
    reply.status(401).send({
      statusCode: 401,
      error: 'Unauthorized',
      message: 'Token verification failed',
    });
  }
}

/**
 * Register authentication plugin with Fastify
 * Protects all routes except public ones
 */
export function registerAuthPlugin(fastify: FastifyInstance) {
  // Public routes that don't require authentication
  const publicRoutes = ['/', '/health', '/api/health'];

  fastify.addHook('onRequest', async (request, reply) => {
    // Skip auth for public routes
    if (publicRoutes.includes(request.url) || request.url.startsWith('/scanner/')) {
      return;
    }

    // Skip auth for OPTIONS requests (CORS preflight)
    if (request.method === 'OPTIONS') {
      return;
    }

    await authenticateRequest(request, reply);
  });
}
