import { buildApp } from '../src/app';
import { supabase } from '../src/lib/supabase';

// Mock Supabase client
jest.mock('../src/lib/supabase', () => ({
  supabase: {
    from: jest.fn(),
  },
}));

// Mock Authentication Middleware
jest.mock('../src/middleware/auth', () => ({
  registerAuthPlugin: (fastify: any) => {
    fastify.addHook('onRequest', async (request: any) => {
      request.user = {
        id: '369e7102-8a9d-4767-850d-8302f30e9227',
        email: 'test@example.com',
        role: 'authenticated',
      };
    });
  },
}));

/**
 * MFA Routes Tests
 */
describe('MFA Routes', () => {
  let app: any;

  beforeAll(async () => {
    app = await buildApp();
  });

  afterAll(async () => {
    if (app) await app.close();
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('GET /mfa/status', () => {
    it('returns MFA status when MFA is not enabled', async () => {
      const mockSingle = jest.fn().mockResolvedValue({
        data: null,
        error: { code: 'PGRST116' },
      });
      const mockEq = jest.fn().mockReturnValue({ single: mockSingle });
      const mockSelect = jest.fn().mockReturnValue({ eq: mockEq });
      (supabase.from as jest.Mock).mockReturnValue({ select: mockSelect });

      const response = await app.inject({
        method: 'GET',
        url: '/mfa/status',
      });

      expect(response.statusCode).toBe(200);
      const body = JSON.parse(response.payload);
      expect(body.success).toBe(true);
    });
  });

  describe('POST /mfa/verify', () => {
    it('returns 400 for missing code', async () => {
      const response = await app.inject({
        method: 'POST',
        url: '/mfa/verify',
        payload: {},
      });

      expect(response.statusCode).toBe(400);
    });

    it('returns 400 for invalid code format', async () => {
      const response = await app.inject({
        method: 'POST',
        url: '/mfa/verify',
        payload: { code: 'abc' },
      });

      expect(response.statusCode).toBe(400);
    });
  });

  describe('POST /mfa/challenge', () => {
    it('returns 400 for missing fields', async () => {
      const response = await app.inject({
        method: 'POST',
        url: '/mfa/challenge',
        payload: {},
      });

      expect(response.statusCode).toBe(400);
    });
  });

  describe('POST /mfa/disable', () => {
    it('returns 400 for missing code', async () => {
      const response = await app.inject({
        method: 'POST',
        url: '/mfa/disable',
        payload: {},
      });

      expect(response.statusCode).toBe(400);
    });
  });
});
