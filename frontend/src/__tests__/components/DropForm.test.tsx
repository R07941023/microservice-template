import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DropForm from '@/components/DropForm';

describe('DropForm', () => {
  const defaultFormData = {
    dropperid: 1001,
    itemid: 2001,
    minimum_quantity: 1,
    maximum_quantity: 5,
    questid: 0,
    chance: 0.5,
    dropper_name: 'Test Monster',
    item_name: 'Test Item',
  };

  const mockOnFormChange = vi.fn();
  const mockOnSubmit = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render all form fields', () => {
    render(
      <DropForm
        formData={defaultFormData}
        onFormChange={mockOnFormChange}
        onSubmit={mockOnSubmit}
        isSubmitting={false}
        submitButtonText="Submit"
        message={null}
      />
    );

    expect(screen.getByText('Dropper ID')).toBeInTheDocument();
    expect(screen.getByText('Item ID')).toBeInTheDocument();
    expect(screen.getByText('Chance')).toBeInTheDocument();
    expect(screen.getByText('Minimum Quantity')).toBeInTheDocument();
    expect(screen.getByText('Maximum Quantity')).toBeInTheDocument();
    expect(screen.getByText('Quest ID')).toBeInTheDocument();
  });

  it('should display form values correctly', () => {
    render(
      <DropForm
        formData={defaultFormData}
        onFormChange={mockOnFormChange}
        onSubmit={mockOnSubmit}
        isSubmitting={false}
        submitButtonText="Submit"
        message={null}
      />
    );

    const inputs = screen.getAllByRole('spinbutton');
    // Order: dropperid, itemid, chance, minimum_quantity, maximum_quantity, questid
    expect(inputs[0]).toHaveValue(1001); // dropperid
    expect(inputs[1]).toHaveValue(2001); // itemid
    expect(inputs[2]).toHaveValue(0.5); // chance
    expect(inputs[3]).toHaveValue(1); // minimum_quantity
    expect(inputs[4]).toHaveValue(5); // maximum_quantity
    expect(inputs[5]).toHaveValue(0); // questid
  });

  it('should call onFormChange when input changes', async () => {
    const user = userEvent.setup();
    render(
      <DropForm
        formData={defaultFormData}
        onFormChange={mockOnFormChange}
        onSubmit={mockOnSubmit}
        isSubmitting={false}
        submitButtonText="Submit"
        message={null}
      />
    );

    const inputs = screen.getAllByRole('spinbutton');
    const dropperIdInput = inputs[0];
    await user.clear(dropperIdInput);
    await user.type(dropperIdInput, '2000');

    expect(mockOnFormChange).toHaveBeenCalled();
  });

  it('should call onSubmit when form is submitted', () => {
    const handleSubmit = vi.fn((e: React.FormEvent) => e.preventDefault());

    render(
      <DropForm
        formData={defaultFormData}
        onFormChange={mockOnFormChange}
        onSubmit={handleSubmit}
        isSubmitting={false}
        submitButtonText="Submit"
        message={null}
      />
    );

    const form = screen.getByRole('button', { name: 'Submit' }).closest('form');
    fireEvent.submit(form!);

    expect(handleSubmit).toHaveBeenCalled();
  });

  it('should display custom submit button text', () => {
    render(
      <DropForm
        formData={defaultFormData}
        onFormChange={mockOnFormChange}
        onSubmit={mockOnSubmit}
        isSubmitting={false}
        submitButtonText="Update Drop"
        message={null}
      />
    );

    expect(screen.getByRole('button', { name: 'Update Drop' })).toBeInTheDocument();
  });

  it('should disable submit button when isSubmitting is true', () => {
    render(
      <DropForm
        formData={defaultFormData}
        onFormChange={mockOnFormChange}
        onSubmit={mockOnSubmit}
        isSubmitting={true}
        submitButtonText="Submit"
        message={null}
      />
    );

    expect(screen.getByRole('button', { name: 'Submit' })).toBeDisabled();
  });

  it('should display success message', () => {
    render(
      <DropForm
        formData={defaultFormData}
        onFormChange={mockOnFormChange}
        onSubmit={mockOnSubmit}
        isSubmitting={false}
        submitButtonText="Submit"
        message="Successfully updated!"
      />
    );

    expect(screen.getByText('Successfully updated!')).toBeInTheDocument();
    expect(screen.getByText('Successfully updated!')).toHaveClass('text-green-500');
  });

  it('should display error message with red styling', () => {
    render(
      <DropForm
        formData={defaultFormData}
        onFormChange={mockOnFormChange}
        onSubmit={mockOnSubmit}
        isSubmitting={false}
        submitButtonText="Submit"
        message="Error: Something went wrong"
      />
    );

    expect(screen.getByText('Error: Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Error: Something went wrong')).toHaveClass('text-red-500');
  });

  it('should render right side content when provided', () => {
    render(
      <DropForm
        formData={defaultFormData}
        onFormChange={mockOnFormChange}
        onSubmit={mockOnSubmit}
        isSubmitting={false}
        submitButtonText="Submit"
        message={null}
        rightSideContent={<button>Delete</button>}
      />
    );

    expect(screen.getByRole('button', { name: 'Delete' })).toBeInTheDocument();
  });

  it('should have required attribute on all inputs', () => {
    render(
      <DropForm
        formData={defaultFormData}
        onFormChange={mockOnFormChange}
        onSubmit={mockOnSubmit}
        isSubmitting={false}
        submitButtonText="Submit"
        message={null}
      />
    );

    const inputs = screen.getAllByRole('spinbutton');
    inputs.forEach((input) => {
      expect(input).toBeRequired();
    });
  });

  it('should have number type on all inputs', () => {
    render(
      <DropForm
        formData={defaultFormData}
        onFormChange={mockOnFormChange}
        onSubmit={mockOnSubmit}
        isSubmitting={false}
        submitButtonText="Submit"
        message={null}
      />
    );

    const inputs = screen.getAllByRole('spinbutton');
    inputs.forEach((input) => {
      expect(input).toHaveAttribute('type', 'number');
    });
  });
});
