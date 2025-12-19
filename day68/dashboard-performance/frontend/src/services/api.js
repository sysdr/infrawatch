import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const dashboardAPI = {
  getWidgets: async (count = 50) => {
    const response = await apiClient.get(`/dashboard/widgets?count=${count}`);
    return response.data;
  },
  
  getWidgetData: async (widgetId, timeRange = '1h', resolution = 100) => {
    const response = await apiClient.get(
      `/dashboard/data/${widgetId}?time_range=${timeRange}&resolution=${resolution}`
    );
    return response.data;
  },
  
  getCacheStats: async () => {
    const response = await apiClient.get('/cache/stats');
    return response.data;
  },
  
  getTimeSeries: async (metric, points = 100) => {
    const response = await apiClient.get(
      `/metrics/timeseries?metric=${metric}&points=${points}`
    );
    return response.data;
  }
};
