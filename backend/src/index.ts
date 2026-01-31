import dotenv from 'dotenv';
import { buildApp, getAllowedOrigins } from './app';
import { SchedulerService } from './lib/scheduler';

// Load environment variables
dotenv.config();

// Start Background Scheduler
const scheduler = new SchedulerService();
scheduler.start();

// Server startup
const PORT = parseInt(process.env.PORT || '3001', 10);

import { logger } from './lib/logger';

// ...

const start = async () => {
  try {
    const app = await buildApp();
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
    console.error('CRITIAL STARTUP ERROR:', err);
    logger.fatal({ err }, 'Failed to start server');
    process.exit(1);
  }
};

start();
