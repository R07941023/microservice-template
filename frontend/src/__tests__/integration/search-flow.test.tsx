import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { DevProvider } from '@/context/DevContext';
import SearchComponent from '@/components/SearchComponent';
import ResultsComponent from '@/components/ResultsComponent';
import { mockDropData, mockNames, mockAlternativeIds } from '../mocks/handlers';
import { server } from '../mocks/server';
import { http, HttpResponse } from 'msw';

// Mock hooks
vi.mock('@/hooks/useClickOutside', () => ({
  useClickOutside: vi.fn(),
}));

vi.mock('@/hooks/useAutocompleteNames', () => ({
  useAutocompleteNames: () => mockNames,
}));

// Mock image components
vi.mock('@/components/MobImageDisplay', () => ({
  default: ({ dropper_name }: { dropper_name: string }) => (
    <div data-testid="mob-image">{dropper_name}</div>
  ),
}));

vi.mock('@/components/ItemImageDisplay', () => ({
  default: ({ item_name }: { item_name: string }) => (
    <div data-testid="item-image">{item_name}</div>
  ),
}));

vi.mock('react-icons/fa', () => ({
  FaCheck: () => <span data-testid="check-icon">check</span>,
  FaTimes: () => <span data-testid="times-icon">times</span>,
}));

// Integration test component that combines Search and Results
const SearchFlowTestComponent: React.FC = () => {
  const [searchTerm, setSearchTerm] = React.useState('');
  const [searchResults, setSearchResults] = React.useState<typeof mockDropData>([]);
  const [alternativeIds, setAlternativeIds] = React.useState<typeof mockAlternativeIds>([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [searchHistory, setSearchHistory] = React.useState<string[]>([]);

  const handleSearch = async (term?: string) => {
    const termToSearch = term || searchTerm;
    if (!termToSearch) return;

    setLoading(true);
    setError(null);
    setSearchResults([]);
    setAlternativeIds([]);

    // Add to history
    if (!searchHistory.includes(termToSearch)) {
      setSearchHistory((prev) => [termToSearch, ...prev].slice(0, 10));
    }

    try {
      const response = await fetch(`/api/search_drops?query=${termToSearch}`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Search failed');
      }

      const data = await response.json();
      setSearchResults(data.data || []);

      // Fetch alternatives if no results
      if (data.data?.length === 0) {
        try {
          const altResponse = await fetch(`/api/existence-check/${termToSearch}`);
          if (altResponse.ok) {
            const altData = await altResponse.json();
            setAlternativeIds(altData.results || []);
          }
        } catch {
          // Ignore alternative fetch errors
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleHistoryClick = (term: string) => {
    setSearchTerm(term);
    handleSearch(term);
  };

  const handleDeleteHistory = (e: React.MouseEvent, term: string) => {
    e.stopPropagation();
    setSearchHistory((prev) => prev.filter((t) => t !== term));
  };

  const handleItemClick = () => {
    // No-op for tests
  };

  return (
    <DevProvider>
      <div data-testid="search-flow-container">
        <SearchComponent
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          handleSearch={handleSearch}
          loading={loading}
          searchHistory={searchHistory}
          handleHistoryClick={handleHistoryClick}
          handleDeleteHistory={handleDeleteHistory}
        />
        <ResultsComponent
          loading={loading}
          error={error}
          searchResults={searchResults}
          searchTerm={searchTerm}
          handleItemClick={handleItemClick}
          alternativeIds={alternativeIds}
        />
      </div>
    </DevProvider>
  );
};

describe('Search Flow Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('should complete full search flow: type -> search -> display results', async () => {
    const user = userEvent.setup();
    render(<SearchFlowTestComponent />);

    // Type in search
    const input = screen.getByPlaceholderText('Search by Dropper ID or Item ID...');
    await user.type(input, 'Test');

    // Click search button
    const searchButton = screen.getByRole('button', { name: 'Search' });
    await user.click(searchButton);

    // Wait for results
    await waitFor(
      () => {
        expect(screen.queryByText('Test Item')).toBeInTheDocument();
      },
      { timeout: 5000 }
    );
  });

  it('should add search term to history after search', async () => {
    const user = userEvent.setup();
    render(<SearchFlowTestComponent />);

    const input = screen.getByPlaceholderText('Search by Dropper ID or Item ID...');
    await user.type(input, 'MySearch');

    const searchButton = screen.getByRole('button', { name: 'Search' });
    await user.click(searchButton);

    // Wait for search to complete and history to appear
    await waitFor(
      () => {
        expect(screen.getByText('MySearch')).toBeInTheDocument();
      },
      { timeout: 5000 }
    );

    expect(screen.getByText('Recent:')).toBeInTheDocument();
  });

  it('should delete history item', async () => {
    const user = userEvent.setup();
    render(<SearchFlowTestComponent />);

    // Add to history
    const input = screen.getByPlaceholderText('Search by Dropper ID or Item ID...');
    await user.type(input, 'ToDelete');
    await user.click(screen.getByRole('button', { name: 'Search' }));

    await waitFor(
      () => {
        expect(screen.getByText('ToDelete')).toBeInTheDocument();
      },
      { timeout: 5000 }
    );

    // Delete from history
    const deleteButton = screen.getByRole('button', { name: /Remove ToDelete/i });
    await user.click(deleteButton);

    expect(screen.queryByText('ToDelete')).not.toBeInTheDocument();
  });

  it('should display error message on search failure', async () => {
    server.use(
      http.get('/api/search_drops', () => {
        return HttpResponse.json({ detail: 'Search service unavailable' }, { status: 500 });
      })
    );

    const user = userEvent.setup();
    render(<SearchFlowTestComponent />);

    const input = screen.getByPlaceholderText('Search by Dropper ID or Item ID...');
    await user.type(input, 'error');
    await user.click(screen.getByRole('button', { name: 'Search' }));

    await waitFor(
      () => {
        expect(screen.getByText(/Error: Search service unavailable/)).toBeInTheDocument();
      },
      { timeout: 5000 }
    );
  });

  it('should show alternative IDs when no results found', async () => {
    server.use(
      http.get('/api/search_drops', () => {
        return HttpResponse.json({ data: [] });
      })
    );

    const user = userEvent.setup();
    render(<SearchFlowTestComponent />);

    const input = screen.getByPlaceholderText('Search by Dropper ID or Item ID...');
    await user.type(input, 'empty');
    await user.click(screen.getByRole('button', { name: 'Search' }));

    await waitFor(
      () => {
        expect(screen.getByText(/the following entries are associated/)).toBeInTheDocument();
      },
      { timeout: 5000 }
    );

    expect(screen.getByRole('table')).toBeInTheDocument();
  });

  it('should show autocomplete suggestions', async () => {
    render(<SearchFlowTestComponent />);

    const input = screen.getByPlaceholderText('Search by Dropper ID or Item ID...');
    fireEvent.change(input, { target: { value: 'Monster' } });
    fireEvent.focus(input);

    await waitFor(() => {
      expect(screen.getByText('Test Monster')).toBeInTheDocument();
    });
  });

  it('should not search with empty input', async () => {
    const user = userEvent.setup();
    render(<SearchFlowTestComponent />);

    const searchButton = screen.getByRole('button', { name: 'Search' });
    await user.click(searchButton);

    // Should not show loading or results
    expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    expect(
      screen.getByText('Enter a Dropper ID or Item ID to search for MapleStory drops.')
    ).toBeInTheDocument();
  });
});
