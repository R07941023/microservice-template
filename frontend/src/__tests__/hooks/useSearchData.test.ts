import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import React from 'react';
import { mockDropData, mockAlternativeIds } from '../mocks/handlers';
import { server } from '../mocks/server';
import { http, HttpResponse } from 'msw';

// Mock contexts before importing the hook
const mockAuthFetch = vi.fn();
const mockDevMode = false;

vi.mock('@/context/AuthContext', () => ({
  useAuth: () => ({
    authFetch: mockAuthFetch,
  }),
}));

vi.mock('@/context/DevContext', () => ({
  useDevMode: () => ({
    devMode: mockDevMode,
  }),
}));

// Import after mocks
import { useSearchData } from '@/hooks/useSearchData';

describe('useSearchData', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();

    // Default mock implementation for authFetch
    mockAuthFetch.mockImplementation(async (url: string, options?: RequestInit) => {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...options?.headers,
          Authorization: 'Bearer mock-token',
        },
      });
      return response;
    });
  });

  it('should initialize with empty values when localStorage is empty', () => {
    const { result } = renderHook(() => useSearchData());

    // The hook triggers an initial search with a default term, but starts empty
    expect(result.current.searchTerm).toBe('');
    expect(result.current.selectedItem).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('should update search term', () => {
    const { result } = renderHook(() => useSearchData());

    act(() => {
      result.current.setSearchTerm('test');
    });

    expect(result.current.searchTerm).toBe('test');
  });

  it('should perform search and update results', async () => {
    const { result } = renderHook(() => useSearchData());

    act(() => {
      result.current.setSearchTerm('Test Monster');
    });

    await act(async () => {
      await result.current.handleSearch();
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.searchResults).toEqual(mockDropData);
    expect(result.current.error).toBeNull();
  });

  it('should add search term to history', async () => {
    const { result } = renderHook(() => useSearchData());

    await act(async () => {
      await result.current.handleSearch('Test Query');
    });

    await waitFor(() => {
      expect(result.current.searchHistory).toContain('Test Query');
    });
  });

  it('should not duplicate entries in search history', async () => {
    const { result } = renderHook(() => useSearchData());

    await act(async () => {
      await result.current.handleSearch('Test Query');
    });

    await act(async () => {
      await result.current.handleSearch('Test Query');
    });

    const occurrences = result.current.searchHistory.filter((t) => t === 'Test Query').length;
    expect(occurrences).toBe(1);
  });

  it('should handle search error', async () => {
    mockAuthFetch.mockImplementation(async () => {
      return {
        ok: false,
        json: async () => ({ detail: 'Search failed' }),
      };
    });

    const { result } = renderHook(() => useSearchData());

    await act(async () => {
      await result.current.handleSearch('error');
    });

    await waitFor(() => {
      expect(result.current.error).toBe('Search failed');
    });
  });

  it('should fetch alternative IDs when no results found', async () => {
    // Return empty results for main search
    server.use(
      http.get('/api/search_drops', () => {
        return HttpResponse.json({ data: [] });
      })
    );

    const { result } = renderHook(() => useSearchData());

    await act(async () => {
      await result.current.handleSearch('empty');
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await waitFor(() => {
      expect(result.current.alternativeIds).toEqual(mockAlternativeIds);
    });
  });

  it('should delete item from history', async () => {
    const { result } = renderHook(() => useSearchData());

    await act(async () => {
      await result.current.handleSearch('Term1');
    });

    await act(async () => {
      await result.current.handleSearch('Term2');
    });

    await waitFor(() => {
      expect(result.current.searchHistory).toContain('Term1');
    });

    const mockEvent = { stopPropagation: vi.fn() } as unknown as React.MouseEvent;

    act(() => {
      result.current.handleDeleteHistory(mockEvent, 'Term1');
    });

    expect(result.current.searchHistory).not.toContain('Term1');
    expect(result.current.searchHistory).toContain('Term2');
  });

  it('should set selected item', () => {
    const { result } = renderHook(() => useSearchData());

    const testItem = mockDropData[0];

    act(() => {
      result.current.setSelectedItem(testItem);
    });

    expect(result.current.selectedItem).toEqual(testItem);
  });

  it('should persist search term to localStorage', async () => {
    const { result } = renderHook(() => useSearchData());

    act(() => {
      result.current.setSearchTerm('persisted');
    });

    await waitFor(() => {
      expect(localStorage.getItem('searchTerm')).toBe('persisted');
    });
  });

  it('should restore search term from localStorage', () => {
    localStorage.setItem('searchTerm', 'restored');

    const { result } = renderHook(() => useSearchData());

    expect(result.current.searchTerm).toBe('restored');
  });

  it('should limit history to 10 items', async () => {
    const { result } = renderHook(() => useSearchData());

    // Add 12 search terms
    for (let i = 0; i < 12; i++) {
      await act(async () => {
        await result.current.handleSearch(`Term${i}`);
      });
    }

    await waitFor(() => {
      expect(result.current.searchHistory.length).toBeLessThanOrEqual(10);
    });
  });

  it('should not call authFetch with empty term', async () => {
    const { result } = renderHook(() => useSearchData());

    // Clear the search term
    act(() => {
      result.current.setSearchTerm('');
    });

    // Clear any previous calls from initial render
    mockAuthFetch.mockClear();

    await act(async () => {
      await result.current.handleSearch('');
    });

    // authFetch should not be called with empty string
    expect(mockAuthFetch).not.toHaveBeenCalledWith(expect.stringContaining('query='), expect.anything());
  });

  it('should clear results on new search', async () => {
    const { result } = renderHook(() => useSearchData());

    // First search
    await act(async () => {
      await result.current.handleSearch('first');
    });

    await waitFor(() => {
      expect(result.current.searchResults.length).toBeGreaterThan(0);
    });

    // Start second search - results should be cleared
    act(() => {
      result.current.handleSearch('second');
    });

    // During loading, results should be cleared
    expect(result.current.searchResults).toEqual([]);
  });
});
