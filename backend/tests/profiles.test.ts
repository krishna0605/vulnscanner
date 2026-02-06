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
 * Profile Routes Tests
 */
describe('Profile Routes', () => {
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

  describe('GET /profiles', () => {
    it('returns list of profiles', async () => {
      const mockProfiles = [
        { id: 'p1', name: 'Quick Scan' },
        { id: 'p2', name: 'Deep Scan' },
      ];
      const mockOrder = jest.fn().mockResolvedValue({
        data: mockProfiles,
        error: null,
      });
      const mockSelect = jest.fn().mockReturnValue({ order: mockOrder });
      (supabase.from as jest.Mock).mockReturnValue({ select: mockSelect });

      const response = await app.inject({
        method: 'GET',
        url: '/profiles',
      });

      expect(response.statusCode).toBe(200);
      const body = JSON.parse(response.payload);
      expect(body.success).toBe(true);
      expect(body.data).toHaveLength(2);
    });
  });

  describe('POST /profiles', () => {
    it('creates a profile successfully', async () => {
      const mockProfile = { id: 'p1', name: 'Test Profile', config: {} };
      const mockSingle = jest.fn().mockResolvedValue({
        data: mockProfile,
        error: null,
      });
      const mockSelect = jest.fn().mockReturnValue({ single: mockSingle });
      const mockInsert = jest.fn().mockReturnValue({ select: mockSelect });
      (supabase.from as jest.Mock).mockReturnValue({ insert: mockInsert });

      const response = await app.inject({
        method: 'POST',
        url: '/profiles',
        payload: {
          name: 'Test Profile',
          config: {},
        },
      });

      expect(response.statusCode).toBe(200);
      const body = JSON.parse(response.payload);
      expect(body.success).toBe(true);
    });

    it('returns 400 for missing name', async () => {
      const response = await app.inject({
        method: 'POST',
        url: '/profiles',
        payload: {
          config: {},
        },
      });

      expect(response.statusCode).toBe(400);
    });
  });

  describe('DELETE /profiles/:id', () => {
    it('deletes a profile successfully', async () => {
      const mockEq = jest.fn().mockResolvedValue({
        data: null,
        error: null,
      });
      const mockDelete = jest.fn().mockReturnValue({ eq: mockEq });
      (supabase.from as jest.Mock).mockReturnValue({ delete: mockDelete });

      const response = await app.inject({
        method: 'DELETE',
        url: '/profiles/a1b2c3d4-5678-90ab-cdef-1234567890ab',
      });

      expect(response.statusCode).toBe(200);
    });

    it('returns 400 for invalid UUID', async () => {
      const response = await app.inject({
        method: 'DELETE',
        url: '/profiles/invalid-uuid',
      });

      expect(response.statusCode).toBe(400);
    });
  });
});
