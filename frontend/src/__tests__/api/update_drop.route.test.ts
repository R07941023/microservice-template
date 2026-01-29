import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { NextRequest } from 'next/server';

// Store original fetch
const originalFetch = global.fetch;

describe('update_drop API Route', () => {
  const mockFetch = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
    global.fetch = mockFetch;
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it('should return 400 when id is missing', async () => {
    const { PUT } = await import('@/app/api/update_drop/[id]/route');

    const request = new NextRequest('http://localhost:3000/api/update_drop/', {
      method: 'PUT',
      body: JSON.stringify({ itemid: 1001 }),
    });

    const context = { params: { id: '' } };
    const response = await PUT(request, context);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data.detail).toBe('Drop ID is required');
  });

  it('should forward PUT request to backend', async () => {
    const mockData = { id: '123', itemid: 1001 };
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const { PUT } = await import('@/app/api/update_drop/[id]/route');

    const body = { itemid: 1001, dropperid: 2001, chance: 0.5 };
    const request = new NextRequest('http://localhost:3000/api/update_drop/123', {
      method: 'PUT',
      body: JSON.stringify(body),
      headers: {
        Authorization: 'Bearer token',
      },
    });

    const context = { params: { id: '123' } };
    await PUT(request, context);

    expect(mockFetch).toHaveBeenCalledWith(
      'http://kong:8000/ms-drop-repo/update_drop/123',
      expect.objectContaining({
        method: 'PUT',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
          Authorization: 'Bearer token',
        }),
        body: JSON.stringify(body),
      })
    );
  });

  it('should include authorization header when present', async () => {
    const mockData = { id: '123' };
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const { PUT } = await import('@/app/api/update_drop/[id]/route');

    const request = new NextRequest('http://localhost:3000/api/update_drop/123', {
      method: 'PUT',
      body: JSON.stringify({ itemid: 1001 }),
      headers: {
        Authorization: 'Bearer my-token',
      },
    });

    const context = { params: { id: '123' } };
    await PUT(request, context);

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
    const errorData = { detail: 'Drop not found' };
    mockFetch.mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => errorData,
    });

    const { PUT } = await import('@/app/api/update_drop/[id]/route');

    const request = new NextRequest('http://localhost:3000/api/update_drop/999', {
      method: 'PUT',
      body: JSON.stringify({ itemid: 1001 }),
    });

    const context = { params: { id: '999' } };
    const response = await PUT(request, context);
    const data = await response.json();

    expect(response.status).toBe(404);
    expect(data.detail).toBe('Drop not found');
  });

  it('should handle backend error without detail', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => ({}),
    });

    const { PUT } = await import('@/app/api/update_drop/[id]/route');

    const request = new NextRequest('http://localhost:3000/api/update_drop/123', {
      method: 'PUT',
      body: JSON.stringify({ itemid: 1001 }),
    });

    const context = { params: { id: '123' } };
    const response = await PUT(request, context);
    const data = await response.json();

    expect(response.status).toBe(500);
    expect(data.detail).toBe('Error updating data in backend');
  });

  it('should handle network error', async () => {
    mockFetch.mockRejectedValue(new Error('Network error'));
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    const { PUT } = await import('@/app/api/update_drop/[id]/route');

    const request = new NextRequest('http://localhost:3000/api/update_drop/123', {
      method: 'PUT',
      body: JSON.stringify({ itemid: 1001 }),
    });

    const context = { params: { id: '123' } };
    const response = await PUT(request, context);
    const data = await response.json();

    expect(response.status).toBe(500);
    expect(data.detail).toBe('Internal Server Error');

    consoleSpy.mockRestore();
  });

  it('should return success response with data', async () => {
    const mockData = { id: '123', itemid: 1001, updated: true };
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const { PUT } = await import('@/app/api/update_drop/[id]/route');

    const request = new NextRequest('http://localhost:3000/api/update_drop/123', {
      method: 'PUT',
      body: JSON.stringify({ itemid: 1001 }),
    });

    const context = { params: { id: '123' } };
    const response = await PUT(request, context);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data).toEqual(mockData);
  });

  it('should handle array id parameter', async () => {
    const mockData = { id: '123' };
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const { PUT } = await import('@/app/api/update_drop/[id]/route');

    const request = new NextRequest('http://localhost:3000/api/update_drop/123', {
      method: 'PUT',
      body: JSON.stringify({ itemid: 1001 }),
    });

    // Test with array id (edge case from Next.js dynamic routes)
    const context = { params: { id: ['123', '456'] } };
    await PUT(request, context);

    // Should use the first element
    expect(mockFetch).toHaveBeenCalledWith(
      'http://kong:8000/ms-drop-repo/update_drop/123',
      expect.any(Object)
    );
  });
});
