import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import React, { ReactNode } from 'react';
import { server } from '../mocks/server';
import { http, HttpResponse } from 'msw';
import { mockNames } from '../mocks/handlers';

// Mock keycloak module at the top level
vi.mock('@/keycloak', () => {
  const mockKeycloak = {
    init: vi.fn().mockResolvedValue(true),
    login: vi.fn(),
    logout: vi.fn(),
    updateToken: vi.fn().mockResolvedValue(true),
    loadUserProfile: vi.fn().mockResolvedValue({
      id: 'test-user-id',
      username: 'testuser',
      email: 'test@example.com',
    }),
    token: 'mock-token',
    authenticated: true,
    tokenParsed: {
      exp: Math.floor(Date.now() / 1000) + 3600,
      sub: 'test-user-id',
    },
    timeSkew: 0,
    onTokenExpired: undefined as (() => void) | undefined,
  };
  return { default: mockKeycloak };
});

// Import after mock
import { useAutocompleteNames } from '@/hooks/useAutocompleteNames';
import { AuthProvider } from '@/context/AuthContext';

// Wrapper component with AuthProvider
const wrapper = ({ children }: { children: ReactNode }) => (
  <AuthProvider>{children}</AuthProvider>
);

describe('useAutocompleteNames', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should return empty array initially', async () => {
    const { result } = renderHook(() => useAutocompleteNames(), { wrapper });

    // Initially empty before fetch completes
    expect(result.current).toEqual([]);
  });

  it('should fetch and return names', async () => {
    const { result } = renderHook(() => useAutocompleteNames(), { wrapper });

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

    const { result } = renderHook(() => useAutocompleteNames(), { wrapper });

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

    const { result } = renderHook(() => useAutocompleteNames(), { wrapper });

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

    const { result } = renderHook(() => useAutocompleteNames(), { wrapper });

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

    const { result } = renderHook(() => useAutocompleteNames(), { wrapper });

    await waitFor(() => {
      // Should fallback to empty array when names is undefined
      expect(result.current).toEqual([]);
    });
  });
});
