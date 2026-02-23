import { describe, it, expect, vi } from 'vitest';

describe('Vitals Rating Logic', () => {
  it('should recognise LCP thresholds', () => {
    const rate = (name, value) => {
      const t = { LCP: [2500, 4000], CLS: [0.1, 0.25], FID: [100, 300], TTFB: [800, 1800], INP: [200, 500] };
      const [g, p] = t[name] || [Infinity, Infinity];
      return value <= g ? 'good' : value <= p ? 'needs-improvement' : 'poor';
    };
    expect(rate('LCP', 1500)).toBe('good');
    expect(rate('LCP', 3000)).toBe('needs-improvement');
    expect(rate('LCP', 5000)).toBe('poor');
    expect(rate('CLS', 0.05)).toBe('good');
    expect(rate('CLS', 0.3)).toBe('poor');
  });
});
