import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

class MetricsService {
  async storeMetric(metricData) {
    try {
      const response = await api.post('/metrics/store', metricData);
      return response.data;
    } catch (error) {
      console.error('Error storing metric:', error);
      throw error;
    }
  }

  async batchStoreMetrics(metricsData) {
    try {
      const response = await api.post('/metrics/batch-store', metricsData);
      return response.data;
    } catch (error) {
      console.error('Error batch storing metrics:', error);
      throw error;
    }
  }

  async queryMetrics(queryParams) {
    try {
      const params = new URLSearchParams();
      params.append('metric_name', queryParams.metric_name);
      params.append('start_time', queryParams.start_time.toISOString());
      params.append('end_time', queryParams.end_time.toISOString());
      
      if (queryParams.tags) {
        params.append('tags', JSON.stringify(queryParams.tags));
      }

      const response = await api.get(`/metrics/query?${params}`);
      return response.data;
    } catch (error) {
      console.error('Error querying metrics:', error);
      throw error;
    }
  }

  async getAggregatedMetrics(metricName, interval, startTime, endTime) {
    try {
      const params = new URLSearchParams();
      params.append('metric_name', metricName);
      params.append('interval', interval);
      params.append('start_time', startTime.toISOString());
      params.append('end_time', endTime.toISOString());

      const response = await api.get(`/metrics/aggregated?${params}`);
      return response.data;
    } catch (error) {
      console.error('Error getting aggregated metrics:', error);
      throw error;
    }
  }

  async searchMetrics(searchTerm, limit = 50) {
    try {
      const params = new URLSearchParams();
      params.append('q', searchTerm);
      params.append('limit', limit);

      const response = await api.get(`/metrics/search?${params}`);
      return response.data.results;
    } catch (error) {
      console.error('Error searching metrics:', error);
      throw error;
    }
  }

  async createAggregations(interval) {
    try {
      const response = await api.post(`/metrics/aggregate/${interval}`);
      return response.data;
    } catch (error) {
      console.error('Error creating aggregations:', error);
      throw error;
    }
  }
}

export default new MetricsService();
