import { create } from 'zustand'
import apiService from '../services/api'

const useNotificationStore = create((set, get) => ({
  // State
  notifications: [],
  preferences: [],
  history: [],
  isLoading: false,
  error: null,

  // Actions
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),

  // Notifications
  fetchNotifications: async (userId = 'demo-user') => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiService.getNotifications(userId)
      // Use fetched notifications as source of truth (API is authoritative)
      set({ 
        notifications: response.notifications || [], 
        isLoading: false 
      })
    } catch (error) {
      set({ 
        error: error.message || 'Failed to fetch notifications', 
        isLoading: false 
      })
    }
  },

  addNotification: (notification) => {
    set(state => {
      // Check if notification already exists
      const exists = state.notifications.some(n => n.id === notification.id)
      if (exists) {
        // Update existing notification instead of adding duplicate
        return {
          notifications: state.notifications.map(n =>
            n.id === notification.id ? notification : n
          )
        }
      }
      // Add new notification at the beginning
      return {
        notifications: [notification, ...state.notifications]
      }
    })
  },

  acknowledgeNotification: async (notificationId) => {
    try {
      await apiService.acknowledgeNotification(notificationId)
      set(state => ({
        notifications: state.notifications.map(notif =>
          notif.id === notificationId
            ? { ...notif, acknowledged: true }
            : notif
        )
      }))
    } catch (error) {
      set({ error: error.message || 'Failed to acknowledge notification' })
    }
  },

  // Preferences
  fetchPreferences: async (userId = 'demo-user') => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiService.getPreferences(userId)
      set({ 
        preferences: response.preferences || [], 
        isLoading: false 
      })
    } catch (error) {
      set({ 
        error: error.message || 'Failed to fetch preferences', 
        isLoading: false 
      })
    }
  },

  updatePreference: async (preferenceId, updateData, userId = 'demo-user') => {
    try {
      await apiService.updatePreference(preferenceId, updateData, userId)
      
      // Update local state
      set(state => ({
        preferences: state.preferences.map(pref =>
          pref.id === preferenceId
            ? { ...pref, ...updateData }
            : pref
        )
      }))
    } catch (error) {
      set({ error: error.message || 'Failed to update preference' })
    }
  },

  // History
  fetchHistory: async (userId = 'demo-user', notificationId = null) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiService.getHistory(userId, notificationId)
      set({ 
        history: response.history || [], 
        isLoading: false 
      })
    } catch (error) {
      set({ 
        error: error.message || 'Failed to fetch history', 
        isLoading: false 
      })
    }
  },

  // Test
  generateTestNotification: async (testType = 'info', userId = 'demo-user') => {
    try {
      const notification = await apiService.generateTestNotification(testType, userId)
      // The notification will be received via WebSocket
      return notification
    } catch (error) {
      set({ error: error.message || 'Failed to generate test notification' })
      throw error
    }
  },

  // Clear error
  clearError: () => set({ error: null }),
}))

export default useNotificationStore
