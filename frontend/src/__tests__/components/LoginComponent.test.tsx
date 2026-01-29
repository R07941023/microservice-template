import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LoginComponent from '@/components/LoginComponent';

// Mock the AuthContext
const mockLogin = vi.fn();
const mockLogout = vi.fn();
let mockAuthState = {
  authenticated: false,
  user: null as { username?: string; email?: string } | null,
  login: mockLogin,
  logout: mockLogout,
};

vi.mock('@/context/AuthContext', () => ({
  useAuth: () => mockAuthState,
}));

describe('LoginComponent', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAuthState = {
      authenticated: false,
      user: null,
      login: mockLogin,
      logout: mockLogout,
    };
  });

  it('should render login button when not authenticated', () => {
    render(<LoginComponent />);

    expect(screen.getByRole('button', { name: 'Login' })).toBeInTheDocument();
  });

  it('should call login when login button is clicked', async () => {
    const user = userEvent.setup();
    render(<LoginComponent />);

    const loginButton = screen.getByRole('button', { name: 'Login' });
    await user.click(loginButton);

    expect(mockLogin).toHaveBeenCalledTimes(1);
  });

  it('should render logout button and username when authenticated', () => {
    mockAuthState = {
      authenticated: true,
      user: { username: 'testuser', email: 'test@example.com' },
      login: mockLogin,
      logout: mockLogout,
    };

    render(<LoginComponent />);

    expect(screen.getByRole('button', { name: 'Logout' })).toBeInTheDocument();
    expect(screen.getByText('testuser')).toBeInTheDocument();
  });

  it('should call logout when logout button is clicked', async () => {
    mockAuthState = {
      authenticated: true,
      user: { username: 'testuser', email: 'test@example.com' },
      login: mockLogin,
      logout: mockLogout,
    };

    const user = userEvent.setup();
    render(<LoginComponent />);

    const logoutButton = screen.getByRole('button', { name: 'Logout' });
    await user.click(logoutButton);

    expect(mockLogout).toHaveBeenCalledTimes(1);
  });

  it('should display email when username is not available', () => {
    mockAuthState = {
      authenticated: true,
      user: { email: 'test@example.com' },
      login: mockLogin,
      logout: mockLogout,
    };

    render(<LoginComponent />);

    expect(screen.getByText('test@example.com')).toBeInTheDocument();
  });

  it('should display "Logged In" when no username or email', () => {
    mockAuthState = {
      authenticated: true,
      user: {},
      login: mockLogin,
      logout: mockLogout,
    };

    render(<LoginComponent />);

    expect(screen.getByText('Logged In')).toBeInTheDocument();
  });

  it('should have correct button styling when not authenticated', () => {
    render(<LoginComponent />);

    const loginButton = screen.getByRole('button', { name: 'Login' });
    expect(loginButton).toHaveClass('bg-blue-500');
  });

  it('should have correct button styling when authenticated', () => {
    mockAuthState = {
      authenticated: true,
      user: { username: 'testuser' },
      login: mockLogin,
      logout: mockLogout,
    };

    render(<LoginComponent />);

    const logoutButton = screen.getByRole('button', { name: 'Logout' });
    expect(logoutButton).toHaveClass('bg-red-500');
  });
});
