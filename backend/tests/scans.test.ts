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
 * Scan Routes Tests
 */
describe('Scan Routes', () => {
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

  describe('POST /scans', () => {
    it('creates a scan successfully', async () => {
      const mockScan = {
        id: 'scan-123',
        project_id: 'a1b2c3d4-5678-90ab-cdef-1234567890ab',
        target_url: 'https://example.com',
        status: 'queued',
      };
      const mockSingle = jest.fn().mockResolvedValue({
        data: mockScan,
        error: null,
      });
      const mockSelect = jest.fn().mockReturnValue({ single: mockSingle });
      const mockInsert = jest.fn().mockReturnValue({ select: mockSelect });
      (supabase.from as jest.Mock).mockReturnValue({ insert: mockInsert });

      const response = await app.inject({
        method: 'POST',
        url: '/scans',
        payload: {
          projectId: 'a1b2c3d4-5678-90ab-cdef-1234567890ab',
          targetUrl: 'https://example.com',
        },
      });

      expect(response.statusCode).toBe(200);
      const body = JSON.parse(response.payload);
      expect(body.success).toBe(true);
    });

    it('returns 400 for missing projectId', async () => {
      const response = await app.inject({
        method: 'POST',
        url: '/scans',
        payload: {
          targetUrl: 'https://example.com',
        },
      });

      expect(response.statusCode).toBe(400);
    });

    it('returns 400 for invalid URL format', async () => {
      const response = await app.inject({
        method: 'POST',
        url: '/scans',
        payload: {
          projectId: 'a1b2c3d4-5678-90ab-cdef-1234567890ab',
          targetUrl: 'not-a-valid-url',
        },
      });

      expect(response.statusCode).toBe(400);
    });
  });

  describe('GET /scans/:id', () => {
    it('returns scan details', async () => {
      const mockScan = {
        id: 'scan-123',
        status: 'completed',
        findings: [],
      };
      const mockSingle = jest.fn().mockResolvedValue({
        data: mockScan,
        error: null,
      });
      const mockEq = jest.fn().mockReturnValue({ single: mockSingle });
      const mockSelect = jest.fn().mockReturnValue({ eq: mockEq });
      (supabase.from as jest.Mock).mockReturnValue({ select: mockSelect });

      const response = await app.inject({
        method: 'GET',
        url: '/scans/a1b2c3d4-5678-90ab-cdef-1234567890ab',
      });

      expect(response.statusCode).toBe(200);
    });

    it('returns 400 for invalid UUID format', async () => {
      const response = await app.inject({
        method: 'GET',
        url: '/scans/not-a-valid-uuid',
      });

      expect(response.statusCode).toBe(400);
    });
  });
});
