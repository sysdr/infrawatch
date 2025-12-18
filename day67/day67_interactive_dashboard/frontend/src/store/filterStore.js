import { create } from 'zustand'
import { addHours, subHours } from 'date-fns'

const useFilterStore = create((set, get) => ({
  // Time range state
  timeRange: {
    start: subHours(new Date(), 24),
    end: new Date(),
    preset: 'last_24h'
  },
  
  // Active filters
  filters: {
    service: null,
    endpoint: null,
    region: null,
    environment: null,
    metric_name: null,
    status: null
  },
  
  // Zoom state
  zoom: {
    min: null,
    max: null
  },
  
  // Drilldown state
  drilldown: {
    level: 0,
    context: {},
    breadcrumbs: []
  },
  
  // Actions
  setTimeRange: (range) => set({ timeRange: range }),
  
  setFilter: (key, value, sourceWidget = null) => set((state) => ({
    filters: { ...state.filters, [key]: value },
    lastFilterSource: sourceWidget
  })),
  
  setMultipleFilters: (filters, sourceWidget = null) => set((state) => ({
    filters: { ...state.filters, ...filters },
    lastFilterSource: sourceWidget
  })),
  
  clearFilter: (key) => set((state) => ({
    filters: { ...state.filters, [key]: null }
  })),
  
  clearAllFilters: () => set({
    filters: {
      service: null,
      endpoint: null,
      region: null,
      environment: null,
      metric_name: null,
      status: null
    },
    drilldown: {
      level: 0,
      context: {},
      breadcrumbs: []
    }
  }),
  
  setZoom: (min, max) => set({ zoom: { min, max } }),
  
  clearZoom: () => set({ zoom: { min: null, max: null } }),
  
  drillDown: (dimension, value) => set((state) => {
    const newContext = { ...state.drilldown.context, [dimension]: value }
    const newLevel = state.drilldown.level + 1
    const newBreadcrumbs = [
      ...state.drilldown.breadcrumbs,
      { dimension, value, level: newLevel }
    ]
    
    return {
      drilldown: {
        level: newLevel,
        context: newContext,
        breadcrumbs: newBreadcrumbs
      },
      filters: { ...state.filters, [dimension]: value }
    }
  }),
  
  drillUp: (toLevel) => set((state) => {
    const newBreadcrumbs = state.drilldown.breadcrumbs.slice(0, toLevel)
    const newContext = {}
    
    newBreadcrumbs.forEach(crumb => {
      newContext[crumb.dimension] = crumb.value
    })
    
    return {
      drilldown: {
        level: toLevel,
        context: newContext,
        breadcrumbs: newBreadcrumbs
      }
    }
  }),
  
  resetDrilldown: () => set({
    drilldown: {
      level: 0,
      context: {},
      breadcrumbs: []
    }
  })
}))

export default useFilterStore
