import '@testing-library/jest-dom';
import { vi } from 'vitest';
// Mock web-vitals
vi.mock('web-vitals', () => ({
  onLCP: vi.fn(),
  onFID: vi.fn(),
  onCLS: vi.fn(),
  onTTFB: vi.fn(),
  onINP: vi.fn(),
}));
