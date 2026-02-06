import { buildApp } from '../src/app';

describe('Health Check', () => {
  let app: any;

  beforeAll(async () => {
    app = await buildApp();
  });

  afterAll(async () => {
    if (app) {
      await app.close();
    }
  });

  it('GET /health returns 200', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/health',
    });
    expect(response.statusCode).toBe(200);
    const payload = JSON.parse(response.payload);
    // Accept both 'healthy' and 'degraded' - DB may not be available in CI
    expect(['healthy', 'degraded']).toContain(payload.status);
  });

  it('GET / returns 200', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/',
    });
    expect(response.statusCode).toBe(200);
    expect(JSON.parse(response.payload)).toHaveProperty('status', 'healthy');
  });
});
