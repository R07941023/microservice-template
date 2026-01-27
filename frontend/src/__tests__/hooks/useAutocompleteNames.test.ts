import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useAutocompleteNames } from '@/hooks/useAutocompleteNames';
import { server } from '../mocks/server';
import { http, HttpResponse } from 'msw';
import { mockNames } from '../mocks/handlers';

describe('useAutocompleteNames', () => {
  it('should return empty array initially', () => {
    const { result } = renderHook(() => useAutocompleteNames());
    expect(result.current).toEqual([]);
  });

  it('should fetch and return names', async () => {
    const { result } = renderHook(() => useAutocompleteNames());

    await waitFor(() => {
      expect(result.current).toEqual(mockNames);
    });
  });

  it('should handle API error gracefully', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    server.use(
      http.get('/api/names/all', () => {
        return HttpResponse.json({ error: 'Server error' }, { status: 500 });
      })
    );

    const { result } = renderHook(() => useAutocompleteNames());

    // Should remain empty on error
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled();
    });

    expect(result.current).toEqual([]);

    consoleSpy.mockRestore();
  });

  it('should handle network error gracefully', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    server.use(
      http.get('/api/names/all', () => {
        return HttpResponse.error();
      })
    );

    const { result } = renderHook(() => useAutocompleteNames());

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled();
    });

    expect(result.current).toEqual([]);

    consoleSpy.mockRestore();
  });

  it('should handle empty names response', async () => {
    server.use(
      http.get('/api/names/all', () => {
        return HttpResponse.json({ names: [] });
      })
    );

    const { result } = renderHook(() => useAutocompleteNames());

    await waitFor(() => {
      expect(result.current).toEqual([]);
    });
  });

  it('should handle missing names property in response', async () => {
    server.use(
      http.get('/api/names/all', () => {
        return HttpResponse.json({});
      })
    );

    const { result } = renderHook(() => useAutocompleteNames());

    await waitFor(() => {
      // Should fallback to empty array when names is undefined
      expect(result.current).toEqual([]);
    });
  });
});
