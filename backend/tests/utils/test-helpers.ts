/**
 * Shared Test Utilities
 * Common mocks, helpers, and fixtures for backend tests
 */

// Mock authenticated user
export const mockUser = {
  id: '369e7102-8a9d-4767-850d-8302f30e9227',
  email: 'test@example.com',
  role: 'authenticated',
};

// Mock project fixture
export const mockProject = {
  id: 'a1b2c3d4-5678-90ab-cdef-1234567890ab',
  name: 'Test Project',
  user_id: mockUser.id,
  description: 'Test project description',
  created_at: new Date().toISOString(),
};

// Mock scan fixture
export const mockScan = {
  id: 'b2c3d4e5-6789-01ab-cdef-234567890abc',
  project_id: mockProject.id,
  target_url: 'https://example.com',
  status: 'queued',
  type: 'quick',
  config: {},
  created_at: new Date().toISOString(),
};

// Mock scan with findings
export const mockScanWithFindings = {
  ...mockScan,
  status: 'completed',
  findings: [
    {
      id: 'f1-uuid',
      scan_id: mockScan.id,
      title: 'XSS Vulnerability',
      severity: 'high',
      description: 'Cross-site scripting detected',
    },
  ],
  assets: [{ count: 5 }],
};

// Mock profile fixture
export const mockProfile = {
  id: 'c3d4e5f6-7890-12ab-cdef-345678901234',
  name: 'Quick Scan Profile',
  description: 'Fast scan with minimal checks',
  config: { maxDepth: 2, maxPages: 50 },
  created_at: new Date().toISOString(),
};

// Helper to create mock Supabase response
export const createMockResponse = <T>(data: T, error: any = null) => ({
  data,
  error,
});

// Helper to create mock error response
export const createMockError = (message: string, code: string = 'DB_ERROR') => ({
  data: null,
  error: { message, code },
});

// Mock Supabase chain helpers
export const createMockChain = (finalResult: any) => {
  const chain: any = {};
  
  // Add chainable methods
  ['select', 'insert', 'update', 'delete', 'eq', 'single', 'order'].forEach(method => {
    chain[method] = jest.fn().mockReturnValue(chain);
  });
  
  // Make the last method in chain resolve
  chain.single = jest.fn().mockResolvedValue(finalResult);
  chain.order = jest.fn().mockResolvedValue(finalResult);
  chain.eq = jest.fn().mockResolvedValue(finalResult);
  
  return chain;
};

// Helper to create mock auth middleware
export const createMockAuthMiddleware = () => ({
  registerAuthPlugin: (fastify: any) => {
    fastify.addHook('onRequest', async (request: any) => {
      request.user = mockUser;
    });
  },
});
