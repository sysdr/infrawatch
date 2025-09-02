const API_BASE_URL = 'http://localhost:8000/api/v1';

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  async getMetrics(params = {}) {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value);
      }
    });

    const queryString = searchParams.toString();
    const endpoint = `/metrics${queryString ? `?${queryString}` : ''}`;
    
    return this.request(endpoint);
  }

  async getMetricNames() {
    return this.request('/metrics/names');
  }

  async createMetric(data) {
    return this.request('/metrics', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export const apiService = new ApiService();
