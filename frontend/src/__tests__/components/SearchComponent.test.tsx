import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SearchComponent from '@/components/SearchComponent';
import { mockNames } from '../mocks/handlers';

// Mock the hooks
vi.mock('@/hooks/useClickOutside', () => ({
  useClickOutside: vi.fn(),
}));

vi.mock('@/hooks/useAutocompleteNames', () => ({
  useAutocompleteNames: () => mockNames,
}));

describe('SearchComponent', () => {
  const defaultProps = {
    searchTerm: '',
    setSearchTerm: vi.fn(),
    handleSearch: vi.fn(),
    loading: false,
    searchHistory: ['Previous Search 1', 'Previous Search 2'],
    handleHistoryClick: vi.fn(),
    handleDeleteHistory: vi.fn(),
    disabled: false,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render search input and button', () => {
    render(<SearchComponent {...defaultProps} />);

    expect(
      screen.getByPlaceholderText('Search by Dropper ID or Item ID...')
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Search' })).toBeInTheDocument();
  });

  it('should render search history', () => {
    render(<SearchComponent {...defaultProps} />);

    expect(screen.getByText('Previous Search 1')).toBeInTheDocument();
    expect(screen.getByText('Previous Search 2')).toBeInTheDocument();
  });

  it('should call setSearchTerm when input changes', async () => {
    const user = userEvent.setup();
    render(<SearchComponent {...defaultProps} />);

    const input = screen.getByPlaceholderText('Search by Dropper ID or Item ID...');
    await user.type(input, 'Test');

    expect(defaultProps.setSearchTerm).toHaveBeenCalled();
  });

  it('should call handleSearch when search button is clicked', async () => {
    const user = userEvent.setup();
    render(<SearchComponent {...defaultProps} searchTerm="test" />);

    const button = screen.getByRole('button', { name: 'Search' });
    await user.click(button);

    expect(defaultProps.handleSearch).toHaveBeenCalled();
  });

  it('should call handleSearch on Enter key press', async () => {
    const handleSearch = vi.fn();
    const user = userEvent.setup();
    render(<SearchComponent {...defaultProps} searchTerm="test" handleSearch={handleSearch} />);

    const input = screen.getByPlaceholderText('Search by Dropper ID or Item ID...');
    await user.click(input);
    await user.keyboard('{Enter}');

    expect(handleSearch).toHaveBeenCalled();
  });

  it('should show loading state', () => {
    render(<SearchComponent {...defaultProps} loading={true} />);

    expect(screen.getByRole('button', { name: 'Searching...' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Searching...' })).toBeDisabled();
  });

  it('should disable inputs when disabled prop is true', () => {
    render(<SearchComponent {...defaultProps} disabled={true} />);

    const input = screen.getByPlaceholderText('Search by Dropper ID or Item ID...');
    const button = screen.getByRole('button', { name: 'Search' });

    expect(input).toBeDisabled();
    expect(button).toBeDisabled();
  });

  it('should call handleHistoryClick when history item is clicked', async () => {
    const user = userEvent.setup();
    render(<SearchComponent {...defaultProps} />);

    const historyItem = screen.getByText('Previous Search 1').closest('div[class*="cursor-pointer"]');
    await user.click(historyItem!);

    expect(defaultProps.handleHistoryClick).toHaveBeenCalledWith('Previous Search 1');
  });

  it('should call handleDeleteHistory when delete button is clicked', async () => {
    const user = userEvent.setup();
    render(<SearchComponent {...defaultProps} />);

    const deleteButtons = screen.getAllByRole('button', {
      name: /Remove .* from history/,
    });
    await user.click(deleteButtons[0]);

    expect(defaultProps.handleDeleteHistory).toHaveBeenCalled();
  });

  it('should show suggestions when input has value and is focused', () => {
    render(<SearchComponent {...defaultProps} />);

    const input = screen.getByPlaceholderText('Search by Dropper ID or Item ID...');

    // Simulate typing to trigger suggestions
    fireEvent.focus(input);
    fireEvent.change(input, { target: { value: 'Test' } });

    // Check for suggestions in the list
    expect(screen.getByText('Test Monster')).toBeInTheDocument();
    expect(screen.getByText('Test Item')).toBeInTheDocument();
  });

  it('should call handleSearch when suggestion is clicked', async () => {
    const user = userEvent.setup();
    render(<SearchComponent {...defaultProps} />);

    const input = screen.getByPlaceholderText('Search by Dropper ID or Item ID...');
    fireEvent.focus(input);
    fireEvent.change(input, { target: { value: 'Test' } });

    // Click on a suggestion
    await user.click(screen.getByText('Test Monster'));

    expect(defaultProps.setSearchTerm).toHaveBeenCalledWith('Test Monster');
    expect(defaultProps.handleSearch).toHaveBeenCalledWith('Test Monster');
  });

  it('should not show history section when history is empty', () => {
    render(<SearchComponent {...defaultProps} searchHistory={[]} />);

    expect(screen.queryByText('Recent:')).not.toBeInTheDocument();
  });

  it('should filter suggestions based on input', () => {
    render(<SearchComponent {...defaultProps} />);

    const input = screen.getByPlaceholderText('Search by Dropper ID or Item ID...');
    fireEvent.focus(input);
    fireEvent.change(input, { target: { value: 'Monster' } });

    expect(screen.getByText('Test Monster')).toBeInTheDocument();
    expect(screen.getByText('Another Monster')).toBeInTheDocument();

    // Items that don't match shouldn't appear in suggestions
    expect(screen.queryByText('Test Item')).not.toBeInTheDocument();
    expect(screen.queryByText('Another Item')).not.toBeInTheDocument();
  });

  it('should not show suggestions when input is empty', () => {
    render(<SearchComponent {...defaultProps} />);

    const input = screen.getByPlaceholderText('Search by Dropper ID or Item ID...');
    fireEvent.focus(input);
    fireEvent.change(input, { target: { value: '' } });

    // Suggestions should not appear for empty input
    const listItems = screen.queryAllByRole('listitem');
    expect(listItems.length).toBe(0);
  });
});
