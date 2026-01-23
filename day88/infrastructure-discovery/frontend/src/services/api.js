import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export const fetchStats = async () => {
  try {
    const response = await axios.get(`${API_BASE}/inventory/stats`);
    return response.data;
  } catch (error) {
    console.error('Error fetching stats:', error);
    return null;
  }
};

export const fetchResources = async (filters = {}) => {
  try {
    const params = new URLSearchParams(filters);
    const response = await axios.get(`${API_BASE}/inventory/resources?${params}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching resources:', error);
    return { resources: [], total: 0 };
  }
};

export const fetchResource = async (resourceId) => {
  try {
    const response = await axios.get(`${API_BASE}/inventory/resources/${resourceId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching resource:', error);
    return null;
  }
};

export const fetchTopology = async () => {
  try {
    const response = await axios.get(`${API_BASE}/topology/graph`);
    return response.data;
  } catch (error) {
    console.error('Error fetching topology:', error);
    return { nodes: [], links: [] };
  }
};

export const fetchDependencies = async (resourceId) => {
  try {
    const response = await axios.get(`${API_BASE}/topology/dependencies/${resourceId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching dependencies:', error);
    return { dependencies: [], total: 0 };
  }
};

export const fetchChanges = async (hours = 24) => {
  try {
    const response = await axios.get(`${API_BASE}/changes/recent?hours=${hours}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching changes:', error);
    return { changes: [], total: 0 };
  }
};

export const fetchChangeStats = async () => {
  try {
    const response = await axios.get(`${API_BASE}/changes/stats`);
    return response.data;
  } catch (error) {
    console.error('Error fetching change stats:', error);
    return null;
  }
};

export const triggerScan = async () => {
  try {
    const response = await axios.post(`${API_BASE}/discovery/scan`);
    return response.data;
  } catch (error) {
    console.error('Error triggering scan:', error);
    return null;
  }
};
