import * as Sentry from '@sentry/node';
import { env } from 'process';

export const initSentry = () => {
  if (process.env.SENTRY_DSN) {
    Sentry.init({
      dsn: process.env.SENTRY_DSN,
      environment: process.env.NODE_ENV || 'development',
      tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
      enabled: process.env.NODE_ENV === 'production',
    });
    console.log('✅ Sentry initialized');
  } else {
    // Silent in dev unless debugging
    if (process.env.NODE_ENV === 'production') {
      console.warn('⚠️ Sentry DSN not found, skipping initialization');
    }
  }
};
