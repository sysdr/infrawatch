import axios from 'axios';

const BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const fetchPerformance = () =>
  axios.get(BASE + '/api/v1/metrics/performance').then(r => r.data);

export const fetchUsers = (params = {}) =>
  axios.get(BASE + '/api/v1/users', { params }).then(r => r.data);

export const fetchTeamAnalytics = () =>
  axios.get(BASE + '/api/v1/users/team-analytics').then(r => r.data);

export const invalidateCache = (tag) =>
  axios.delete(BASE + '/api/v1/users/cache/invalidate', { params: { tag } }).then(r => r.data);
