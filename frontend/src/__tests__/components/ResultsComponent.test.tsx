import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ResultsComponent from '@/components/ResultsComponent';
import { DropData, AggregatedExistenceInfo } from '@/hooks/useSearchData';

// Mock ItemCard component
vi.mock('@/components/ItemCard', () => ({
  default: ({
    item,
    onClick,
  }: {
    item: DropData;
    onClick: (item: DropData) => void;
  }) => (
    <div data-testid={`item-card-${item.id}`} onClick={() => onClick(item)}>
      {item.item_name}
    </div>
  ),
}));

// Mock react-icons
vi.mock('react-icons/fa', () => ({
  FaCheck: () => <span data-testid="check-icon">check</span>,
  FaTimes: () => <span data-testid="times-icon">times</span>,
}));

describe('ResultsComponent', () => {
  const mockSearchResults: DropData[] = [
    {
      id: '1',
      dropperid: 1001,
      itemid: 2001,
      minimum_quantity: 1,
      maximum_quantity: 5,
      questid: 0,
      chance: 0.5,
      dropper_name: 'Test Monster',
      item_name: 'Test Item',
    },
    {
      id: '2',
      dropperid: 1002,
      itemid: 2002,
      minimum_quantity: 1,
      maximum_quantity: 10,
      questid: 100,
      chance: 0.25,
      dropper_name: 'Test Monster 2',
      item_name: 'Test Item 2',
    },
  ];

  const mockAlternativeIds: AggregatedExistenceInfo[] = [
    { id: 1001, type: 'mob', image_exist: true, drop_exist: true },
    { id: 2001, type: 'item', image_exist: true, drop_exist: false },
  ];

  const mockHandleItemClick = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should show loading state', () => {
    render(
      <ResultsComponent
        loading={true}
        error={null}
        searchResults={[]}
        searchTerm=""
        handleItemClick={mockHandleItemClick}
      />
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('should show error message', () => {
    render(
      <ResultsComponent
        loading={false}
        error="Something went wrong"
        searchResults={[]}
        searchTerm=""
        handleItemClick={mockHandleItemClick}
      />
    );

    expect(screen.getByText('Error: Something went wrong')).toBeInTheDocument();
  });

  it('should show search results', () => {
    render(
      <ResultsComponent
        loading={false}
        error={null}
        searchResults={mockSearchResults}
        searchTerm="test"
        handleItemClick={mockHandleItemClick}
      />
    );

    expect(screen.getByTestId('item-card-1')).toBeInTheDocument();
    expect(screen.getByTestId('item-card-2')).toBeInTheDocument();
    expect(screen.getByText('Test Item')).toBeInTheDocument();
    expect(screen.getByText('Test Item 2')).toBeInTheDocument();
  });

  it('should call handleItemClick when item card is clicked', () => {
    render(
      <ResultsComponent
        loading={false}
        error={null}
        searchResults={mockSearchResults}
        searchTerm="test"
        handleItemClick={mockHandleItemClick}
      />
    );

    fireEvent.click(screen.getByTestId('item-card-1'));

    expect(mockHandleItemClick).toHaveBeenCalledWith(mockSearchResults[0]);
  });

  it('should show no results message when search term exists but no results', () => {
    render(
      <ResultsComponent
        loading={false}
        error={null}
        searchResults={[]}
        searchTerm="nonexistent"
        handleItemClick={mockHandleItemClick}
      />
    );

    expect(screen.getByText(/No results found for/)).toBeInTheDocument();
    expect(screen.getByText(/nonexistent/)).toBeInTheDocument();
  });

  it('should show alternative IDs table when no results but alternatives exist', () => {
    render(
      <ResultsComponent
        loading={false}
        error={null}
        searchResults={[]}
        searchTerm="test"
        handleItemClick={mockHandleItemClick}
        alternativeIds={mockAlternativeIds}
      />
    );

    expect(screen.getByText(/However, the following entries are associated/)).toBeInTheDocument();
    expect(screen.getByRole('table')).toBeInTheDocument();
    expect(screen.getByText('mob')).toBeInTheDocument();
    expect(screen.getByText('item')).toBeInTheDocument();
    expect(screen.getByText('1001')).toBeInTheDocument();
    expect(screen.getByText('2001')).toBeInTheDocument();
  });

  it('should show check icons for true values and times icons for false values', () => {
    render(
      <ResultsComponent
        loading={false}
        error={null}
        searchResults={[]}
        searchTerm="test"
        handleItemClick={mockHandleItemClick}
        alternativeIds={mockAlternativeIds}
      />
    );

    const checkIcons = screen.getAllByTestId('check-icon');
    const timesIcons = screen.getAllByTestId('times-icon');

    // First entry: image_exist=true, drop_exist=true (2 checks)
    // Second entry: image_exist=true, drop_exist=false (1 check, 1 times)
    expect(checkIcons.length).toBe(3);
    expect(timesIcons.length).toBe(1);
  });

  it('should show prompt to search when no search term and no results', () => {
    render(
      <ResultsComponent
        loading={false}
        error={null}
        searchResults={[]}
        searchTerm=""
        handleItemClick={mockHandleItemClick}
      />
    );

    expect(
      screen.getByText('Enter a Dropper ID or Item ID to search for MapleStory drops.')
    ).toBeInTheDocument();
  });

  it('should prioritize error over other states', () => {
    render(
      <ResultsComponent
        loading={true}
        error="Error message"
        searchResults={mockSearchResults}
        searchTerm="test"
        handleItemClick={mockHandleItemClick}
      />
    );

    expect(screen.getByText('Error: Error message')).toBeInTheDocument();
    expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
  });

  it('should render grid layout for results', () => {
    const { container } = render(
      <ResultsComponent
        loading={false}
        error={null}
        searchResults={mockSearchResults}
        searchTerm="test"
        handleItemClick={mockHandleItemClick}
      />
    );

    const grid = container.querySelector('.grid');
    expect(grid).toBeInTheDocument();
    expect(grid).toHaveClass('grid-cols-1');
  });
});
