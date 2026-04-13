import axios from 'axios';
const API = axios.create({ baseURL: '/api', timeout: 10000 });
export const usersApi = {
  list: () => API.get('/users'),
  create: (d) => API.post('/users', d),
  get: (id) => API.get(`/users/${id}`),
};
export const vapidApi = {
  getPublicKey: () => API.get('/vapid/public-key'),
};
export const subscriptionsApi = {
  create: (d) => API.post('/subscriptions', d),
  getUserSubs: (uid) => API.get(`/subscriptions/user/${uid}`),
  delete: (id) => API.delete(`/subscriptions/${id}`),
};
export const notificationsApi = {
  send: (d) => API.post('/notifications/send', d),
  recordEvent: (d) => API.post('/notifications/event', d),
  getAnalytics: () => API.get('/notifications/analytics'),
  getPreferences: (uid) => API.get(`/notifications/preferences/${uid}`),
  updatePreferences: (uid, d) => API.patch(`/notifications/preferences/${uid}`, d),
  snooze: (d) => API.post('/notifications/snooze', d),
  clearSnooze: (uid) => API.delete(`/notifications/snooze/${uid}`),
};
