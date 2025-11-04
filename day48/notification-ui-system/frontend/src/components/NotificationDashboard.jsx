import React, { useState, useEffect } from 'react'
import { Bell, Settings, History, TestTube, Wifi, WifiOff } from 'lucide-react'
import NotificationCenter from './NotificationCenter/NotificationCenter'
import PreferenceManager from './PreferenceManager/PreferenceManager'
import NotificationHistory from './NotificationHistory/NotificationHistory'
import TestGenerator from './TestGenerator/TestGenerator'
import useWebSocket from '../hooks/useWebSocket'
import useNotificationStore from '../store/notificationStore'

const NotificationDashboard = () => {
  const [activeTab, setActiveTab] = useState('notifications')
  const { isConnected, messages, acknowledgeNotification } = useWebSocket(
    'ws://localhost:8000/ws'
  )
  
  const {
    fetchNotifications,
    fetchPreferences,
    fetchHistory,
    addNotification,
    acknowledgeNotification: storeAcknowledge
  } = useNotificationStore()

  useEffect(() => {
    // Initial data fetch
    fetchNotifications()
    fetchPreferences()
    fetchHistory()
  }, [])

  useEffect(() => {
    // Handle incoming WebSocket messages
    messages.forEach(message => {
      if (message.type === 'notification') {
        addNotification(message.data)
      }
    })
  }, [messages, addNotification])

  const handleAcknowledge = async (notificationId) => {
    await storeAcknowledge(notificationId)
    acknowledgeNotification(notificationId)
  }

  const tabs = [
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'preferences', label: 'Preferences', icon: Settings },
    { id: 'history', label: 'History', icon: History },
    { id: 'test', label: 'Test Generator', icon: TestTube },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Notification Center
              </h1>
              <p className="text-gray-600 mt-2">
                Manage your notifications, preferences, and system alerts
              </p>
            </div>
            
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              {isConnected ? (
                <>
                  <Wifi className="w-5 h-5 text-green-500" />
                  <span className="text-sm text-green-600 font-medium">Connected</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-5 h-5 text-red-500" />
                  <span className="text-sm text-red-600 font-medium">Disconnected</span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 min-h-[600px]">
          {activeTab === 'notifications' && (
            <NotificationCenter onAcknowledge={handleAcknowledge} />
          )}
          {activeTab === 'preferences' && <PreferenceManager />}
          {activeTab === 'history' && <NotificationHistory />}
          {activeTab === 'test' && <TestGenerator />}
        </div>
      </div>
    </div>
  )
}

export default NotificationDashboard
