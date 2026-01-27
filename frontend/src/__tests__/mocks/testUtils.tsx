import React, { ReactElement, ReactNode } from 'react';
import { render, RenderOptions, RenderResult } from '@testing-library/react';
import { AuthProvider } from '@/context/AuthContext';
import { DevProvider } from '@/context/DevContext';
import { vi } from 'vitest';

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
  }),
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
  useParams: () => ({}),
}));

// Type for mock auth context
interface MockAuthContextValue {
  user: { username: string; email: string } | null;
  token: string | null;
  authenticated: boolean;
  loading: boolean;
  login: () => void;
  logout: () => void;
  authFetch: (url: string, options?: RequestInit) => Promise<Response>;
}

// Create mock auth context value
export const createMockAuthContext = (
  overrides: Partial<MockAuthContextValue> = {}
): MockAuthContextValue => ({
  user: { username: 'testuser', email: 'test@example.com' },
  token: 'mock-token',
  authenticated: true,
  loading: false,
  login: vi.fn(),
  logout: vi.fn(),
  authFetch: vi.fn().mockImplementation((url: string, options?: RequestInit) =>
    fetch(url, {
      ...options,
      headers: {
        ...options?.headers,
        Authorization: 'Bearer mock-token',
      },
    })
  ),
  ...overrides,
});

// Mock AuthContext for testing
const MockAuthContext = React.createContext<MockAuthContextValue | undefined>(undefined);

// Mock AuthProvider that uses provided values
interface MockAuthProviderProps {
  children: ReactNode;
  value?: Partial<MockAuthContextValue>;
}

export const MockAuthProvider: React.FC<MockAuthProviderProps> = ({ children, value = {} }) => {
  const contextValue = createMockAuthContext(value);
  return <MockAuthContext.Provider value={contextValue}>{children}</MockAuthContext.Provider>;
};

// Export mock useAuth hook
export const useMockAuth = () => {
  const context = React.useContext(MockAuthContext);
  if (!context) {
    throw new Error('useMockAuth must be used within MockAuthProvider');
  }
  return context;
};

// Provider wrapper options
interface WrapperOptions {
  authValue?: Partial<MockAuthContextValue>;
  withDevProvider?: boolean;
  initialDevMode?: boolean;
}

// Create wrapper with providers
const createWrapper = (options: WrapperOptions = {}) => {
  const { authValue, withDevProvider = true, initialDevMode = false } = options;

  // Set initial localStorage value for dev mode if needed
  if (initialDevMode) {
    localStorage.setItem('devMode', JSON.stringify(true));
  }

  const Wrapper: React.FC<{ children: ReactNode }> = ({ children }) => {
    let content = children;

    if (withDevProvider) {
      content = <DevProvider>{content}</DevProvider>;
    }

    // Use mock auth provider for testing (avoids Keycloak initialization)
    content = <MockAuthProvider value={authValue}>{content}</MockAuthProvider>;

    return <>{content}</>;
  };

  return Wrapper;
};

// Custom render function with providers
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  wrapperOptions?: WrapperOptions;
}

export const renderWithProviders = (
  ui: ReactElement,
  { wrapperOptions, ...renderOptions }: CustomRenderOptions = {}
): RenderResult => {
  const Wrapper = createWrapper(wrapperOptions);
  return render(ui, { wrapper: Wrapper, ...renderOptions });
};

// Render with real AuthProvider (for integration tests)
export const renderWithRealProviders = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
): RenderResult => {
  const Wrapper: React.FC<{ children: ReactNode }> = ({ children }) => (
    <DevProvider>
      <AuthProvider>{children}</AuthProvider>
    </DevProvider>
  );
  return render(ui, { wrapper: Wrapper, ...options });
};

// Re-export testing library utilities
export * from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';
