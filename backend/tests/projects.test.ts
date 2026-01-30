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
      // Inject mock user for every request in tests
      request.user = {
        id: '369e7102-8a9d-4767-850d-8302f30e9227',
        email: 'test@example.com',
        role: 'authenticated',
      };
    });
  },
}));

describe('Project Routes', () => {
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

  it('POST /projects creates a project successfully', async () => {
    // Mock the chain: .from().insert().select().single()
    const mockSingle = jest.fn().mockResolvedValue({
      data: { id: 'p-1', name: 'Test Project', user_id: '369e7102-8a9d-4767-850d-8302f30e9227' },
      error: null,
    });
    const mockSelect = jest.fn().mockReturnValue({ single: mockSingle });
    const mockInsert = jest.fn().mockReturnValue({ select: mockSelect });

    (supabase.from as jest.Mock).mockReturnValue({
      insert: mockInsert,
    });

    const response = await app.inject({
      method: 'POST',
      url: '/projects',
      payload: {
        name: 'Test Project',
        description: 'A test project',
        // No userId needed, handled by middleware
      },
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.payload);
    expect(body.success).toBe(true);
    expect(body.data.name).toBe('Test Project');
  });

  it('POST /projects returns 400 for invalid input', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/projects',
      payload: {
        // Name is missing
        description: 'Missing name',
      },
    });

    expect(response.statusCode).toBe(400);
    const body = JSON.parse(response.payload);
    expect(body.success).toBe(false);
    expect(body.error.code).toBe('VALIDATION_ERROR');
  });

  it('GET /projects lists user projects', async () => {
    // Mock chain: .from().select().eq()
    const mockEq = jest.fn().mockResolvedValue({
      data: [
        { id: 'p-1', name: 'Project A', user_id: '369e7102-8a9d-4767-850d-8302f30e9227' },
        { id: 'p-2', name: 'Project B', user_id: '369e7102-8a9d-4767-850d-8302f30e9227' },
      ],
      error: null,
    });
    const mockSelect = jest.fn().mockReturnValue({ eq: mockEq });
    (supabase.from as jest.Mock).mockReturnValue({
      select: mockSelect,
    });

    const response = await app.inject({
      method: 'GET',
      url: '/projects',
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.payload);
    expect(body.success).toBe(true);
    expect(body.data).toHaveLength(2);
    expect(body.data[0].name).toBe('Project A');
  });
});
