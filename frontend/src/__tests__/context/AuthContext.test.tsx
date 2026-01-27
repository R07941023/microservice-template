import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';

// Mock keycloak module at the top level
vi.mock('@/keycloak', () => {
  const mockKeycloak = {
    init: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
    updateToken: vi.fn(),
    loadUserProfile: vi.fn(),
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

// Import the mocked module to access it
import keycloak from '@/keycloak';
import { AuthProvider, useAuth } from '@/context/AuthContext';

// Get reference to mocked keycloak
const mockKeycloak = keycloak as unknown as {
  init: ReturnType<typeof vi.fn>;
  login: ReturnType<typeof vi.fn>;
  logout: ReturnType<typeof vi.fn>;
  updateToken: ReturnType<typeof vi.fn>;
  loadUserProfile: ReturnType<typeof vi.fn>;
  token: string;
  authenticated: boolean;
  tokenParsed: { exp: number; sub: string };
  timeSkew: number;
  onTokenExpired: (() => void) | undefined;
};

// Test component to consume the context
const TestConsumer = () => {
  const { user, token, authenticated, loading, login, logout, authFetch } = useAuth();

  const handleTestFetch = async () => {
    try {
      await authFetch('/api/test');
    } catch {
      // Error handled in component
    }
  };

  return (
    <div>
      <span data-testid="loading">{loading ? 'loading' : 'loaded'}</span>
      <span data-testid="authenticated">{authenticated ? 'true' : 'false'}</span>
      <span data-testid="token">{token || 'no-token'}</span>
      <span data-testid="username">{user?.username || 'no-user'}</span>
      <button onClick={login}>Login</button>
      <button onClick={logout}>Logout</button>
      <button onClick={handleTestFetch}>Test Fetch</button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockKeycloak.init.mockResolvedValue(true);
    mockKeycloak.loadUserProfile.mockResolvedValue({
      username: 'testuser',
      email: 'test@example.com',
    });
    mockKeycloak.token = 'mock-token';
    mockKeycloak.authenticated = true;
  });

  it('should show loading state initially', () => {
    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    expect(screen.getByTestId('loading')).toHaveTextContent('loading');
  });

  it('should initialize keycloak and set authenticated state', async () => {
    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('loaded');
    });

    expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
    expect(screen.getByTestId('token')).toHaveTextContent('mock-token');
    expect(screen.getByTestId('username')).toHaveTextContent('testuser');
  });

  it('should call keycloak.login when login is called', async () => {
    const user = userEvent.setup();
    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('loaded');
    });

    await user.click(screen.getByRole('button', { name: 'Login' }));

    expect(mockKeycloak.login).toHaveBeenCalled();
  });

  it('should call keycloak.logout when logout is called', async () => {
    const user = userEvent.setup();
    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('loaded');
    });

    await user.click(screen.getByRole('button', { name: 'Logout' }));

    expect(mockKeycloak.logout).toHaveBeenCalled();
  });

  it('should handle keycloak init failure', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    mockKeycloak.init.mockRejectedValue(new Error('Init failed'));

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('loaded');
    });

    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
    consoleSpy.mockRestore();
  });

  it('should handle unauthenticated state', async () => {
    mockKeycloak.init.mockResolvedValue(false);

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('loaded');
    });

    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
  });

  it('should throw error when useAuth is used outside provider', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => {
      render(<TestConsumer />);
    }).toThrow('useAuth must be used within an AuthProvider');

    consoleSpy.mockRestore();
  });

  it('should add authorization header in authFetch', async () => {
    const fetchSpy = vi.spyOn(global, 'fetch').mockResolvedValue(new Response('OK'));
    const user = userEvent.setup();

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('loaded');
    });

    await user.click(screen.getByRole('button', { name: 'Test Fetch' }));

    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/test',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer mock-token',
        }),
      })
    );

    fetchSpy.mockRestore();
  });

  it('should redirect to login on 401 response', async () => {
    const fetchSpy = vi.spyOn(global, 'fetch').mockResolvedValue(
      new Response('Unauthorized', { status: 401 })
    );
    const user = userEvent.setup();

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('loaded');
    });

    await user.click(screen.getByRole('button', { name: 'Test Fetch' }));

    expect(mockKeycloak.login).toHaveBeenCalled();

    fetchSpy.mockRestore();
  });
});
