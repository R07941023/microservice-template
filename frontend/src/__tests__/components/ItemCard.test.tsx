import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ItemCard from '@/components/ItemCard';

// Mock the image components
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

describe('ItemCard', () => {
  const mockItem = {
    id: '1',
    dropperid: 1001,
    itemid: 2001,
    minimum_quantity: 1,
    maximum_quantity: 5,
    questid: 0,
    chance: 0.5,
    dropper_name: 'Test Monster',
    item_name: 'Test Item',
  };

  const mockOnClick = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render item card with all information', () => {
    render(<ItemCard item={mockItem} onClick={mockOnClick} />);

    // Check for the dropper name (appears in two places: mob image mock and text)
    expect(screen.getAllByText('Test Monster').length).toBeGreaterThan(0);
    // Check for the item name
    expect(screen.getAllByText('Test Item').length).toBeGreaterThan(0);
    expect(screen.getByText('Chance: 0.5')).toBeInTheDocument();
    expect(screen.getByText('Quantity: 1 - 5')).toBeInTheDocument();
  });

  it('should render mob and item images', () => {
    render(<ItemCard item={mockItem} onClick={mockOnClick} />);

    expect(screen.getByTestId('mob-image')).toBeInTheDocument();
    expect(screen.getByTestId('item-image')).toBeInTheDocument();
  });

  it('should call onClick when card is clicked', () => {
    const { container } = render(<ItemCard item={mockItem} onClick={mockOnClick} />);

    // Click the card container (first child div)
    const card = container.firstChild as HTMLElement;
    fireEvent.click(card);

    expect(mockOnClick).toHaveBeenCalledTimes(1);
    expect(mockOnClick).toHaveBeenCalledWith(mockItem);
  });

  it('should display correct quantity range', () => {
    const itemWithRange = {
      ...mockItem,
      minimum_quantity: 10,
      maximum_quantity: 100,
    };

    render(<ItemCard item={itemWithRange} onClick={mockOnClick} />);

    expect(screen.getByText('Quantity: 10 - 100')).toBeInTheDocument();
  });

  it('should display decimal chance values', () => {
    const itemWithDecimalChance = {
      ...mockItem,
      chance: 0.0001,
    };

    render(<ItemCard item={itemWithDecimalChance} onClick={mockOnClick} />);

    expect(screen.getByText('Chance: 0.0001')).toBeInTheDocument();
  });

  it('should have correct styling classes', () => {
    const { container } = render(<ItemCard item={mockItem} onClick={mockOnClick} />);

    const card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('border', 'rounded-lg', 'cursor-pointer');
  });
});
