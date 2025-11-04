import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
    })
    
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )
    
    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response.data,
      (error) => {
        console.error('API Error:', error)
        return Promise.reject(error)
      }
    )
  }

  // Notifications
  async getNotifications(userId = 'demo-user', limit = 50) {
    return this.client.get(`/notifications?user_id=${userId}&limit=${limit}`)
  }

  async createNotification(notificationData) {
    return this.client.post('/notifications', notificationData)
  }

  async acknowledgeNotification(notificationId) {
    return this.client.put(`/notifications/${notificationId}/acknowledge`)
  }

  // Preferences
  async getPreferences(userId = 'demo-user') {
    return this.client.get(`/preferences?user_id=${userId}`)
  }

  async updatePreference(preferenceId, updateData, userId = 'demo-user') {
    return this.client.put(`/preferences/${preferenceId}?user_id=${userId}`, updateData)
  }

  // History
  async getHistory(userId = 'demo-user', notificationId = null) {
    let url = `/history?user_id=${userId}`
    if (notificationId) {
      url += `&notification_id=${notificationId}`
    }
    return this.client.get(url)
  }

  // Test
  async generateTestNotification(testType = 'info', userId = 'demo-user') {
    return this.client.post(`/test/notification?test_type=${testType}&user_id=${userId}`)
  }

  async getTestTypes() {
    return this.client.get('/test/types')
  }
}

export default new ApiService()
