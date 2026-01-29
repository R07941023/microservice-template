import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DevProvider, useDevMode } from '@/context/DevContext';

// Test component to consume the context
const TestConsumer = () => {
  const { devMode, toggleDevMode } = useDevMode();
  return (
    <div>
      <span data-testid="dev-mode">{devMode ? 'true' : 'false'}</span>
      <button onClick={toggleDevMode}>Toggle</button>
    </div>
  );
};

describe('DevContext', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should provide default devMode as false', () => {
    render(
      <DevProvider>
        <TestConsumer />
      </DevProvider>
    );

    expect(screen.getByTestId('dev-mode')).toHaveTextContent('false');
  });

  it('should toggle devMode when toggleDevMode is called', async () => {
    const user = userEvent.setup();
    render(
      <DevProvider>
        <TestConsumer />
      </DevProvider>
    );

    expect(screen.getByTestId('dev-mode')).toHaveTextContent('false');

    await user.click(screen.getByRole('button', { name: 'Toggle' }));

    expect(screen.getByTestId('dev-mode')).toHaveTextContent('true');
  });

  it('should toggle back to false', async () => {
    const user = userEvent.setup();
    render(
      <DevProvider>
        <TestConsumer />
      </DevProvider>
    );

    await user.click(screen.getByRole('button', { name: 'Toggle' }));
    expect(screen.getByTestId('dev-mode')).toHaveTextContent('true');

    await user.click(screen.getByRole('button', { name: 'Toggle' }));
    expect(screen.getByTestId('dev-mode')).toHaveTextContent('false');
  });

  it('should persist devMode to localStorage', async () => {
    const user = userEvent.setup();
    render(
      <DevProvider>
        <TestConsumer />
      </DevProvider>
    );

    await user.click(screen.getByRole('button', { name: 'Toggle' }));

    expect(localStorage.getItem('devMode')).toBe('true');
  });

  it('should initialize from localStorage', () => {
    localStorage.setItem('devMode', 'true');

    render(
      <DevProvider>
        <TestConsumer />
      </DevProvider>
    );

    expect(screen.getByTestId('dev-mode')).toHaveTextContent('true');
  });

  it('should throw error when useDevMode is used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => {
      render(<TestConsumer />);
    }).toThrow('useDevMode must be used within a DevProvider');

    consoleSpy.mockRestore();
  });
});
