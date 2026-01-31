import * as Sentry from '@sentry/nextjs';

type LogLevel = 'info' | 'warn' | 'error' | 'debug';

class Logger {
  private log(level: LogLevel, message: string, context?: object) {
    const timestamp = new Date().toISOString();

    // In development, pretty print to console
    if (process.env.NODE_ENV === 'development') {
      const color = {
        info: '\x1b[36m', // Cyan
        warn: '\x1b[33m', // Yellow
        error: '\x1b[31m', // Red
        debug: '\x1b[90m', // Gray
      }[level];
      const reset = '\x1b[0m';

      console[level](`${color}[${level.toUpperCase()}]${reset} ${message}`, context || '');
    } else {
      // In production, log JSON
      console[level](
        JSON.stringify({
          timestamp,
          level,
          message,
          ...context,
        })
      );
    }

    // Report to Sentry for errors and warnings
    if (level === 'error' || level === 'warn') {
      Sentry.withScope((scope) => {
        if (context) {
          scope.setExtras(context as Record<string, any>);
        }
        scope.setLevel(level as Sentry.SeverityLevel);
        Sentry.captureMessage(message);
      });
    }
  }

  public info(message: string, context?: object) {
    this.log('info', message, context);
  }

  public warn(message: string, context?: object) {
    this.log('warn', message, context);
  }

  public error(message: string, context?: object) {
    this.log('error', message, context);
  }

  public debug(message: string, context?: object) {
    this.log('debug', message, context);
  }
}

export const logger = new Logger();
