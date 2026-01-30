import Fastify, { FastifyInstance } from 'fastify';
import cors from '@fastify/cors';
import rateLimit from '@fastify/rate-limit';
import helmet from '@fastify/helmet';
import { projectRoutes } from './routes/projects';
import { scanRoutes } from './routes/scans';
import { profileRoutes } from './routes/profiles';
import { registerAuthPlugin } from './middleware/auth';
import { AppError } from './lib/errors';
import { z } from 'zod';
import * as Sentry from '@sentry/node';
import { initSentry } from './lib/sentry';
import { env, isProduction, isDevelopment } from './lib/env';

// Parse allowed origins from environment variable
export const getAllowedOrigins = (): string[] | boolean => {
  if (!env.ALLOWED_ORIGINS) {
    // In development, allow localhost origins
    if (isDevelopment) {
      return ['http://localhost:3000', 'http://127.0.0.1:3000'];
    }
    // In production with no config, deny all cross-origin
    return false;
  }
  return env.ALLOWED_ORIGINS.split(',').map((o) => o.trim());
};

import { registerRequestId } from './middleware/request-id';

export async function buildApp(): Promise<FastifyInstance> {
  // Initialize Sentry
  initSentry();

  const fastify = Fastify({
    logger: {
      level: env.LOG_LEVEL,
      transport: isDevelopment
        ? {
            target: 'pino-pretty',
            options: {
              translateTime: 'HH:MM:ss Z',
              ignore: 'pid,hostname',
            },
          }
        : undefined,
    },
    // Generate request IDs if not present, useful for tracing
    genReqId: (req) => (req.headers['x-request-id'] as string) || crypto.randomUUID(),
  });

  // Register Request ID middleware early to ensure it's available
  registerRequestId(fastify);

  // Register Helmet for security headers
  fastify.register(helmet, {
    contentSecurityPolicy: isProduction
      ? {
          directives: {
            defaultSrc: ["'self'"],
            scriptSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'"],
            imgSrc: ["'self'", 'data:', 'https:'],
            connectSrc: ["'self'", 'https://*.supabase.co'],
          },
        }
      : false, // Disable CSP in development for easier debugging
    crossOriginEmbedderPolicy: false, // Needed for some resources
  });

  // Register Swagger (OpenAPI)
  await fastify.register(import('@fastify/swagger'), {
    openapi: {
      info: {
        title: 'VulnScanner API',
        description: 'AI-Powered URL Threat Intelligence & Vulnerability Analysis',
        version: '1.0.0',
      },
      servers: [{ url: 'http://localhost:3001' }],
      components: {
        securitySchemes: {
          bearerAuth: {
            type: 'http',
            scheme: 'bearer',
            bearerFormat: 'JWT',
          },
        },
        schemas: {
          // Reusable schemas
          Error: {
            type: 'object',
            properties: {
              success: { type: 'boolean', const: false },
              error: {
                type: 'object',
                properties: {
                  code: { type: 'string' },
                  message: { type: 'string' },
                },
              },
            },
          },
          Success: {
            type: 'object',
            properties: {
              success: { type: 'boolean', const: true },
              data: { type: 'object' },
            },
          },
        },
      },
      tags: [
        { name: 'Scans', description: 'Vulnerability scan operations' },
        { name: 'Projects', description: 'Project management' },
        { name: 'Profiles', description: 'Scan profile configuration' },
      ],
    },
  });

  await fastify.register(import('@fastify/swagger-ui'), {
    routePrefix: '/docs',
    uiConfig: {
      docExpansion: 'list',
      deepLinking: false,
    },
  });

  // Register CORS with restrictive configuration
  fastify.register(cors, {
    origin: getAllowedOrigins(),
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  });

  // Register Rate Limiting
  fastify.register(rateLimit, {
    max: env.RATE_LIMIT_MAX,
    timeWindow: env.RATE_LIMIT_WINDOW_MS,
    errorResponseBuilder: (request, context) => ({
      statusCode: 429,
      error: 'Too Many Requests',
      message: `Rate limit exceeded. You can make ${context.max} requests per ${context.after}. Please try again later.`,
    }),
  });

  // Register Authentication Plugin (protects all non-public routes)
  registerAuthPlugin(fastify);

  // Audit Logging - log all requests for security monitoring
  fastify.addHook('onResponse', (request, reply, done) => {
    // Skip logging for health checks to reduce noise
    if (request.url === '/' || request.url === '/health') {
      done();
      return;
    }

    const sensitizeBody = (body: any) => {
      if (!body) return body;
      try {
        const sensitized = { ...body };
        const sensitiveFields = ['password', 'authPassword', 'token', 'key', 'secret'];

        // Recursive sanitization could be added here if needed
        for (const field of sensitiveFields) {
          if (field in sensitized) sensitized[field] = '[REDACTED]';
        }

        // Handle config object specifically for scan creates
        if (sensitized.config) {
          if (sensitized.config.authPassword) sensitized.config.authPassword = '[REDACTED]';
        }

        return sensitized;
      } catch {
        return body;
      }
    };

    const logData = {
      timestamp: new Date().toISOString(),
      method: request.method,
      url: request.url,
      statusCode: reply.statusCode,
      responseTime: Math.round(reply.elapsedTime),
      userId: (request as any).user?.id || 'anonymous',
      ip: request.ip,
      // Log sanitized body only on errors or for debug
      body: reply.statusCode >= 400 ? sensitizeBody(request.body) : undefined,
      userAgent: request.headers['user-agent']?.substring(0, 100),
    };

    // Log based on status code severity with structured data
    if (reply.statusCode >= 500) {
      request.log.error({ ...logData, err: (request as any).error }, 'Server error');
    } else if (reply.statusCode >= 400) {
      request.log.warn(logData, 'Client error');
    } else {
      request.log.info(logData, 'Request completed');
    }

    done();
  });

  // Global Error Handler
  fastify.setErrorHandler((error, request, reply) => {
    // Capture error in Sentry
    Sentry.withScope((scope) => {
      scope.setTag('path', request.url);
      scope.setTag('method', request.method);
      scope.setExtra('requestId', request.id);
      if ((request as any).user) {
        scope.setUser({ id: (request as any).user.id });
      }
      Sentry.captureException(error);
    });

    // Log full error for debugging with request ID
    request.log.error(
      {
        err: error,
        requestId: request.id,
        url: request.url,
        method: request.method,
      },
      'Request failed'
    );

    // Handle known AppErrors
    if (error instanceof AppError) {
      return reply.status(error.statusCode).send({
        success: false,
        error: {
          code: error.code,
          message: error.message,
          ...(isDevelopment && { stack: error.stack }),
        },
      });
    }

    // Handle Zod validation errors
    if (error instanceof z.ZodError) {
      return reply.status(400).send({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Invalid request data',
          details: error.errors,
        },
      });
    }

    // Handle Fastify schema validation errors
    if (error.code === 'FST_ERR_VALIDATION') {
      return reply.status(400).send({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: error.message,
        },
      });
    }

    // Handle unknown errors - ensure no sensitive details leak in production
    return reply.status(500).send({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: 'An unexpected error occurred',
      },
    });
  });

  // Register routes
  fastify.register(projectRoutes);
  fastify.register(scanRoutes);
  fastify.register(profileRoutes);

  // Health check endpoints (public, no auth required)
  fastify.get('/', async function handler(request, reply) {
    return { status: 'healthy', timestamp: new Date().toISOString() };
  });

  fastify.get('/health', async function handler(request, reply) {
    const startTime = Date.now();
    let dbStatus: 'healthy' | 'unhealthy' = 'unhealthy';
    let dbLatency = 0;

    // Check database connectivity
    try {
      const { createClient } = await import('@supabase/supabase-js');
      const supabase = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY);
      const dbStart = Date.now();
      const { error } = await supabase.from('projects').select('id').limit(1);
      dbLatency = Date.now() - dbStart;
      dbStatus = error ? 'unhealthy' : 'healthy';
    } catch (e) {
      request.log.warn({ err: e }, 'Health check: database connectivity failed');
    }

    const overallStatus = dbStatus === 'healthy' ? 'healthy' : 'degraded';

    return {
      status: overallStatus,
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      version: process.env.npm_package_version || '1.0.0',
      checks: {
        database: {
          status: dbStatus,
          latency_ms: dbLatency,
        },
      },
      memory: {
        heapUsed: Math.round(process.memoryUsage().heapUsed / 1024 / 1024) + ' MB',
        heapTotal: Math.round(process.memoryUsage().heapTotal / 1024 / 1024) + ' MB',
      },
    };
  });

  return fastify;
}
