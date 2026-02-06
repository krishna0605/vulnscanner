/**
 * Jest Test Setup
 * Polyfills and global configuration for tests
 */
import { webcrypto } from 'crypto';

// Polyfill crypto.randomUUID for Node.js test environment
// This is needed because Jest runs in Node which doesn't have the global crypto API
// available in older Node versions, but the app uses crypto.randomUUID()
if (typeof global.crypto === 'undefined') {
  (global as any).crypto = webcrypto;
}
