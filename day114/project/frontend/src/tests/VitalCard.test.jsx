import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import VitalCard from '../components/performance/VitalCard';

describe('VitalCard', () => {
  it('renders LCP value and rating', () => {
    render(<VitalCard metric="LCP" stats={{ avg: 1800, min: 900, max: 3200, count: 42, rating: 'good' }} />);
    expect(screen.getByText('Largest Contentful Paint')).toBeInTheDocument();
    expect(screen.getByText('good')).toBeInTheDocument();
  });

  it('renders nothing when stats is null', () => {
    const { container } = render(<VitalCard metric="LCP" stats={null} />);
    expect(container.firstChild).toBeNull();
  });
});
