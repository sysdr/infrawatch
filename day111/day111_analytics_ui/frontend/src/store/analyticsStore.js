import { create } from 'zustand';

const useAnalyticsStore = create((set) => ({
  // Dashboard
  kpis: [],
  dashboardState: 'LOADING',
  lastUpdated: null,
  setKpis: (kpis, updatedAt) => set({ kpis, lastUpdated: updatedAt, dashboardState: 'READY' }),
  setDashboardState: (s) => set({ dashboardState: s }),

  // ML
  mlState: 'IDLE',
  mlResult: null,
  setMlResult: (r) => set({ mlResult: r, mlState: 'ML_RESULT' }),
  setMlState: (s) => set({ mlState: s }),

  // Correlation
  corrState: 'IDLE',
  corrMatrix: null,
  corrLabels: [],
  setCorrResult: (matrix, labels) => set({ corrMatrix: matrix, corrLabels: labels, corrState: 'CORR_DONE' }),
  setCorrState: (s) => set({ corrState: s }),

  // Reports
  reports: [],
  setReports: (r) => set({ reports: r }),

  // Config
  config: {},
  setConfig: (c) => set({ config: c }),
}));

export default useAnalyticsStore;
