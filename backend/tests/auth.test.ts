import { buildApp } from '../src/app';

/**
 * Authentication Middleware Tests
 */
describe('Authentication Middleware', () => {
  let app: any;

  beforeAll(async () => {
    app = await buildApp();
  });

  afterAll(async () => {
    if (app) await app.close();
  });

  describe('Public Routes', () => {
    it('allows access to / without authentication', async () => {
      const response = await app.inject({
        method: 'GET',
        url: '/',
      });

      expect(response.statusCode).toBe(200);
    });

    it('allows access to /health without authentication', async () => {
      const response = await app.inject({
        method: 'GET',
        url: '/health',
      });

      expect(response.statusCode).toBe(200);
    });
  });
});
