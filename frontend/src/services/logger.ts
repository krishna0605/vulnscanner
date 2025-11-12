// Lightweight logger that gates debug/info in production builds
// Works with CRA (process.env.NODE_ENV) and future Vite migration (import.meta.env.MODE)

const isProd = (() => {
  try {
    // CRA
    if (typeof process !== 'undefined' && process.env && process.env.NODE_ENV) {
      return process.env.NODE_ENV === 'production';
    }
    // Vite fallback
    if (typeof import.meta !== 'undefined' && (import.meta as any).env?.MODE) {
      return (import.meta as any).env.MODE === 'production';
    }
  } catch (_) {
    // no-op
  }
  return false;
})();

export const logger = {
  debug: (...args: unknown[]) => {
    if (!isProd) {
      // eslint-disable-next-line no-console
      console.debug(...args);
    }
  },
  info: (...args: unknown[]) => {
    if (!isProd) {
      // eslint-disable-next-line no-console
      console.info(...args);
    }
  },
  warn: (...args: unknown[]) => {
    // eslint-disable-next-line no-console
    console.warn(...args);
  },
  error: (...args: unknown[]) => {
    // eslint-disable-next-line no-console
    console.error(...args);
  },
};

export default logger;