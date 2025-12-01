import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyticsApi = {
  getChartData: async (params) => {
    const response = await api.get('/api/analytics/chart', { params });
    return response.data;
  },
  
  getTimeseriesData: async (metric, channels, hours) => {
    const response = await api.get('/api/analytics/chart/timeseries', {
      params: { metric, channels, hours }
    });
    return response.data;
  },
  
  getTrends: async (metric, channel, days) => {
    const response = await api.get('/api/analytics/trends', {
      params: { metric, channel, days }
    });
    return response.data;
  },
  
  compareMetrics: async (metric, dimensions, days) => {
    const response = await api.get('/api/analytics/compare', {
      params: { metric, dimensions, days }
    });
    return response.data;
  },
  
  compareChannels: async (metric, channels, days) => {
    const response = await api.get('/api/analytics/compare/channels', {
      params: { metric, channels, days }
    });
    return response.data;
  },
  
  drillDown: async (level, dimension, parentFilters, days) => {
    const response = await api.get('/api/analytics/drilldown', {
      params: {
        level,
        dimension,
        parent_filters: JSON.stringify(parentFilters),
        days
      }
    });
    return response.data;
  },
};

export default api;
