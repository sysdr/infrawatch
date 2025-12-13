import axios from 'axios';

const API_BASE = '/api/charts';

export const chartService = {
  async getMultiSeriesData(metrics) {
    const params = new URLSearchParams();
    metrics.forEach(m => params.append('metrics', m));
    const response = await axios.get(`${API_BASE}/multi-series?${params}`);
    return response.data;
  },

  async getStackedData(categories, series) {
    const params = new URLSearchParams();
    categories.forEach(c => params.append('categories', c));
    series.forEach(s => params.append('series', s));
    const response = await axios.get(`${API_BASE}/stacked?${params}`);
    return response.data;
  },

  async getScatterData(xMetric, yMetric) {
    const response = await axios.get(
      `${API_BASE}/scatter?x_metric=${xMetric}&y_metric=${yMetric}&samples=1000`
    );
    return response.data;
  },

  async getHeatmapData(metric, days = 7) {
    const response = await axios.get(`${API_BASE}/heatmap?metric=${metric}&days=${days}`);
    return response.data;
  },

  async getLatencyDistribution() {
    const response = await axios.get(`${API_BASE}/custom/latency-distribution`);
    return response.data;
  },

  async getStatusTimeline(hours = 24) {
    const response = await axios.get(`${API_BASE}/custom/status-timeline?hours=${hours}`);
    return response.data;
  }
};
