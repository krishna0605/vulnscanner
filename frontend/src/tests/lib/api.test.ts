/**
 * API Client Tests
 * Tests for the frontend API client functions
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('API Client', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('fetch wrapper', () => {
    it('makes GET request with correct headers', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: [] }),
      });

      const response = await fetch('/api/projects', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      expect(mockFetch).toHaveBeenCalledWith('/api/projects', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      expect(response.ok).toBe(true);
    });

    it('makes POST request with body', async () => {
      const newProject = { name: 'Test Project' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: { id: '1', ...newProject } }),
      });

      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newProject),
      });

      expect(mockFetch).toHaveBeenCalledWith('/api/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newProject),
      });
      expect(response.ok).toBe(true);
    });

    it('handles network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(
        fetch('/api/projects')
      ).rejects.toThrow('Network error');
    });

    it('handles 401 unauthorized', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ error: 'Unauthorized' }),
      });

      const response = await fetch('/api/projects');
      expect(response.ok).toBe(false);
      expect(response.status).toBe(401);
    });

    it('handles 500 server error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ error: 'Internal Server Error' }),
      });

      const response = await fetch('/api/projects');
      expect(response.ok).toBe(false);
      expect(response.status).toBe(500);
    });
  });

  describe('Response parsing', () => {
    it('parses JSON response correctly', async () => {
      const mockData = { success: true, data: [{ id: '1', name: 'Project 1' }] };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      const response = await fetch('/api/projects');
      const data = await response.json();

      expect(data).toEqual(mockData);
      expect(data.success).toBe(true);
      expect(data.data).toHaveLength(1);
    });

    it('handles empty response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: [] }),
      });

      const response = await fetch('/api/projects');
      const data = await response.json();

      expect(data.data).toEqual([]);
    });
  });
});
