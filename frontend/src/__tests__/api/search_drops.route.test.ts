import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { NextResponse } from 'next/server';

// These tests use manual fetch mocking (not MSW) since they test internal API routes
// that make external requests. We mock fetch directly to control backend responses.

// Store original fetch
const originalFetch = global.fetch;

describe('search_drops API Route', () => {
  const mockFetch = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
    // Replace global fetch with mock
    global.fetch = mockFetch;
  });

  afterEach(() => {
    // Restore original fetch
    global.fetch = originalFetch;
  });

  it('should return 400 when query parameter is missing', async () => {
    const { GET } = await import('@/app/api/search_drops/route');

    const request = new Request('http://localhost:3000/api/search_drops');
    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data.detail).toBe("Query parameter 'query' is required.");
  });

  it('should forward request to Kong when dev mode is off', async () => {
    const mockData = { data: [{ id: '1', item_name: 'Test Item' }] };
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const { GET } = await import('@/app/api/search_drops/route');

    const request = new Request('http://localhost:3000/api/search_drops?query=test', {
      headers: {
        Authorization: 'Bearer token',
        'X-Dev-Mode': 'false',
      },
    });

    await GET(request);

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('http://kong:8000/ms-search-aggregator/search/test'),
      expect.objectContaining({
        method: 'GET',
        cache: 'no-store',
      })
    );
  });

  it('should forward request to drops-augmented endpoint when dev mode is on', async () => {
    const mockData = { data: [{ id: '1', item_name: 'Test Item' }] };
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const { GET } = await import('@/app/api/search_drops/route');

    const request = new Request('http://localhost:3000/api/search_drops?query=test', {
      headers: {
        Authorization: 'Bearer token',
        'X-Dev-Mode': 'true',
      },
    });

    await GET(request);

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('http://kong:8000/ms-search-aggregator/api/search/drops-augmented'),
      expect.any(Object)
    );
  });

  it('should include authorization header in backend request', async () => {
    const mockData = { data: [] };
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const { GET } = await import('@/app/api/search_drops/route');

    const request = new Request('http://localhost:3000/api/search_drops?query=test', {
      headers: {
        Authorization: 'Bearer my-token',
      },
    });

    await GET(request);

    expect(mockFetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer my-token',
        }),
      })
    );
  });

  it('should handle backend error response', async () => {
    const errorData = { detail: 'Backend error' };
    mockFetch.mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => errorData,
    });

    const { GET } = await import('@/app/api/search_drops/route');

    const request = new Request('http://localhost:3000/api/search_drops?query=test');
    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(500);
    expect(data.detail).toBe('Backend error');
  });

  it('should handle network error', async () => {
    mockFetch.mockRejectedValue(new Error('Network error'));
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    const { GET } = await import('@/app/api/search_drops/route');

    const request = new Request('http://localhost:3000/api/search_drops?query=test');
    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(500);
    expect(data.detail).toBe('Internal Server Error');

    consoleSpy.mockRestore();
  });

  it('should return data on successful response', async () => {
    const mockData = { data: [{ id: '1', item_name: 'Test' }] };
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const { GET } = await import('@/app/api/search_drops/route');

    const request = new Request('http://localhost:3000/api/search_drops?query=test');
    const response = await GET(request);
    const data = await response.json();

    expect(data).toEqual(mockData);
  });
});
