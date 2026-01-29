import { vi } from 'vitest';

// Mock Keycloak user profile
export const mockUser = {
  id: 'test-user-id',
  username: 'testuser',
  email: 'test@example.com',
  firstName: 'Test',
  lastName: 'User',
};

// Mock token
export const mockToken = 'mock-jwt-token';

// Create a mock Keycloak instance
export const createMockKeycloak = (overrides = {}) => ({
  init: vi.fn().mockResolvedValue(true),
  login: vi.fn(),
  logout: vi.fn(),
  updateToken: vi.fn().mockResolvedValue(true),
  loadUserProfile: vi.fn().mockResolvedValue(mockUser),
  token: mockToken,
  authenticated: true,
  tokenParsed: {
    exp: Math.floor(Date.now() / 1000) + 3600,
    sub: mockUser.id,
  },
  timeSkew: 0,
  onTokenExpired: undefined as (() => void) | undefined,
  ...overrides,
});

// Default mock instance
export const mockKeycloak = createMockKeycloak();

// Mock the keycloak-js module
vi.mock('keycloak-js', () => ({
  default: vi.fn().mockImplementation(() => mockKeycloak),
}));

// Mock the @/keycloak module
vi.mock('@/keycloak', () => ({
  default: mockKeycloak,
}));
