import { create } from 'zustand';

export const useDashboardStore = create((set) => ({
  metrics: [],
  performance: null,
  displayMetrics: {},
  
  updateMetrics: (newMetrics) => set((state) => {
    // Group metrics by name for display
    const grouped = {};
    const allMetrics = [...state.metrics, ...newMetrics].slice(-1000); // Keep last 1000
    
    allMetrics.forEach(metric => {
      if (!grouped[metric.name]) {
        grouped[metric.name] = [];
      }
      grouped[metric.name].push(metric);
    });
    
    // Keep only last 100 points per metric for display
    Object.keys(grouped).forEach(key => {
      grouped[key] = grouped[key].slice(-100);
    });
    
    return {
      metrics: allMetrics,
      displayMetrics: grouped
    };
  }),
  
  updatePerformance: (stats) => set({ performance: stats }),
  
  clearMetrics: () => set({ metrics: [], displayMetrics: {} })
}));
