// Load environment variables FIRST before any other imports
import dotenv from 'dotenv';
dotenv.config();

// Log environment status immediately
console.log('[Startup] Environment check:');
console.log('  - PORT:', process.env.PORT || '(not set, using 3001)');
console.log('  - NODE_ENV:', process.env.NODE_ENV || '(not set)');
console.log('  - SUPABASE_URL:', process.env.SUPABASE_URL ? 'SET' : 'MISSING');
console.log('  - SUPABASE_SERVICE_ROLE_KEY:', process.env.SUPABASE_SERVICE_ROLE_KEY ? 'SET' : 'MISSING');
console.log('  - ALLOWED_ORIGINS:', process.env.ALLOWED_ORIGINS || '(not set)');

import { buildApp, getAllowedOrigins } from './app';
import { SchedulerService } from './lib/scheduler';
import { logger } from './lib/logger';

// Server startup
const PORT = parseInt(process.env.PORT || '3001', 10);

const start = async () => {
  try {
    console.log('[Startup] Building app...');
    const app = await buildApp();
    
    console.log('[Startup] Starting scheduler...');
    const scheduler = new SchedulerService();
    scheduler.start();
    
    console.log(`[Startup] Binding to 0.0.0.0:${PORT}...`);
    await app.listen({ port: PORT, host: '0.0.0.0' });

    // Use Fastify's logger for server startup info
    app.log.info(
      {
        port: PORT,
        corsOrigins: getAllowedOrigins(),
        rateLimit: `${process.env.RATE_LIMIT_MAX || '100'} req/min`,
        security: {
          helmet: true,
          jwtAuth: true,
          auditLog: true,
        },
      },
      '🚀 Server started successfully'
    );
  } catch (err) {
    console.error('CRITICAL STARTUP ERROR:', err);
    logger.fatal({ err }, 'Failed to start server');
    process.exit(1);
  }
};

start();
