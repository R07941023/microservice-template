import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { NextRequest } from 'next/server';

// Store original fetch
const originalFetch = global.fetch;

describe('chat API Route', () => {
  const mockFetch = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
    global.fetch = mockFetch;
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it('should return 400 when prompt is missing', async () => {
    const { POST } = await import('@/app/api/chat/route');

    const request = new NextRequest('http://localhost:3000/api/chat', {
      method: 'POST',
      body: JSON.stringify({}),
    });

    const response = await POST(request);

    expect(response.status).toBe(400);
    const text = await response.text();
    expect(text).toBe('Prompt is required');
  });

  it('should forward request to orchestrator service', async () => {
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode('Hello'));
        controller.close();
      },
    });

    mockFetch.mockResolvedValue({
      ok: true,
      body: stream,
    });

    const { POST } = await import('@/app/api/chat/route');

    const request = new NextRequest('http://localhost:3000/api/chat', {
      method: 'POST',
      body: JSON.stringify({ prompt: 'Hello AI' }),
      headers: {
        Authorization: 'Bearer token',
      },
    });

    await POST(request);

    expect(mockFetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
          Authorization: 'Bearer token',
        }),
        body: JSON.stringify({ prompt: 'Hello AI' }),
      })
    );
  });

  it('should return streaming response', async () => {
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode('Test response'));
        controller.close();
      },
    });

    mockFetch.mockResolvedValue({
      ok: true,
      body: stream,
    });

    const { POST } = await import('@/app/api/chat/route');

    const request = new NextRequest('http://localhost:3000/api/chat', {
      method: 'POST',
      body: JSON.stringify({ prompt: 'Test' }),
    });

    const response = await POST(request);

    expect(response.headers.get('Content-Type')).toBe('text/plain; charset=utf-8');
  });

  it('should handle orchestrator service error', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 500,
      text: async () => 'Service unavailable',
    });

    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    const { POST } = await import('@/app/api/chat/route');

    const request = new NextRequest('http://localhost:3000/api/chat', {
      method: 'POST',
      body: JSON.stringify({ prompt: 'Test' }),
    });

    const response = await POST(request);

    expect(response.status).toBe(500);

    consoleSpy.mockRestore();
  });

  it('should return 500 when response body is empty', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      body: null,
    });

    const { POST } = await import('@/app/api/chat/route');

    const request = new NextRequest('http://localhost:3000/api/chat', {
      method: 'POST',
      body: JSON.stringify({ prompt: 'Test' }),
    });

    const response = await POST(request);

    expect(response.status).toBe(500);
    const text = await response.text();
    expect(text).toBe('Empty response body from the service');
  });

  it('should handle network error', async () => {
    mockFetch.mockRejectedValue(new Error('Network error'));
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    const { POST } = await import('@/app/api/chat/route');

    const request = new NextRequest('http://localhost:3000/api/chat', {
      method: 'POST',
      body: JSON.stringify({ prompt: 'Test' }),
    });

    const response = await POST(request);

    expect(response.status).toBe(500);
    const text = await response.text();
    expect(text).toBe('An internal server error occurred.');

    consoleSpy.mockRestore();
  });

  it('should include Authorization header when present', async () => {
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode('OK'));
        controller.close();
      },
    });

    mockFetch.mockResolvedValue({
      ok: true,
      body: stream,
    });

    const { POST } = await import('@/app/api/chat/route');

    const request = new NextRequest('http://localhost:3000/api/chat', {
      method: 'POST',
      body: JSON.stringify({ prompt: 'Test' }),
      headers: {
        Authorization: 'Bearer my-jwt-token',
      },
    });

    await POST(request);

    expect(mockFetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer my-jwt-token',
        }),
      })
    );
  });
});
