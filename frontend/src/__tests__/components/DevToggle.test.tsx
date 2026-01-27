import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DevToggle from '@/components/DevToggle';

// Mock the DevContext
const mockToggleDevMode = vi.fn();
let mockDevMode = false;

vi.mock('@/context/DevContext', () => ({
  useDevMode: () => ({
    devMode: mockDevMode,
    toggleDevMode: mockToggleDevMode,
  }),
}));

describe('DevToggle', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockDevMode = false;
  });

  it('should render toggle switch', () => {
    render(<DevToggle />);

    expect(screen.getByRole('checkbox')).toBeInTheDocument();
    expect(screen.getByText('Dev')).toBeInTheDocument();
  });

  it('should show unchecked state when devMode is false', () => {
    mockDevMode = false;
    render(<DevToggle />);

    const checkbox = screen.getByRole('checkbox');
    expect(checkbox).not.toBeChecked();
  });

  it('should show checked state when devMode is true', () => {
    mockDevMode = true;
    render(<DevToggle />);

    const checkbox = screen.getByRole('checkbox');
    expect(checkbox).toBeChecked();
  });

  it('should call toggleDevMode when clicked', async () => {
    const user = userEvent.setup();
    render(<DevToggle />);

    const checkbox = screen.getByRole('checkbox');
    await user.click(checkbox);

    expect(mockToggleDevMode).toHaveBeenCalledTimes(1);
  });

  it('should have blue background when devMode is true', () => {
    mockDevMode = true;
    const { container } = render(<DevToggle />);

    const toggleBackground = container.querySelector('.bg-blue-600');
    expect(toggleBackground).toBeInTheDocument();
  });

  it('should have gray background when devMode is false', () => {
    mockDevMode = false;
    const { container } = render(<DevToggle />);

    const toggleBackground = container.querySelector('.bg-gray-600');
    expect(toggleBackground).toBeInTheDocument();
  });

  it('should have fixed position at bottom-left', () => {
    const { container } = render(<DevToggle />);

    const toggleContainer = container.firstChild as HTMLElement;
    expect(toggleContainer).toHaveClass('fixed', 'bottom-4', 'left-4');
  });

  it('should have sr-only class on checkbox for accessibility', () => {
    render(<DevToggle />);

    const checkbox = screen.getByRole('checkbox');
    expect(checkbox).toHaveClass('sr-only');
  });

  it('should translate dot when devMode is true', () => {
    mockDevMode = true;
    const { container } = render(<DevToggle />);

    const dot = container.querySelector('.dot');
    expect(dot).toHaveClass('translate-x-full');
  });

  it('should not translate dot when devMode is false', () => {
    mockDevMode = false;
    const { container } = render(<DevToggle />);

    const dot = container.querySelector('.dot');
    expect(dot).not.toHaveClass('translate-x-full');
  });
});
