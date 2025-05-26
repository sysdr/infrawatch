import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ProductCard from '../ProductCard';
import { Product } from '../../../types/Product';

const mockProduct: Product = {
  id: 1,
  name: 'Test Product',
  price: 29.99,
  description: 'Test description',
  category: 'Electronics',
  inStock: true,
  createdAt: '2024-01-01T00:00:00Z',
};

const mockOnEdit = jest.fn();
const mockOnDelete = jest.fn();

describe('ProductCard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders product information correctly', () => {
    render(
      <ProductCard
        product={mockProduct}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText('Test Product')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
    expect(screen.getByText('$29.99')).toBeInTheDocument();
    expect(screen.getByText('Electronics')).toBeInTheDocument();
    expect(screen.getByText('In Stock')).toBeInTheDocument();
  });

  test('calls onEdit when edit button is clicked', () => {
    render(
      <ProductCard
        product={mockProduct}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    fireEvent.click(screen.getByText('Edit'));
    expect(mockOnEdit).toHaveBeenCalledWith(mockProduct);
  });

  test('calls onDelete when delete button is clicked', () => {
    render(
      <ProductCard
        product={mockProduct}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    fireEvent.click(screen.getByText('Delete'));
    expect(mockOnDelete).toHaveBeenCalledWith(1);
  });
});
