import React, { useState, useEffect } from 'react'
import { Settings, Save, RotateCcw, Bell, Mail, MessageSquare, Smartphone } from 'lucide-react'
import useNotificationStore from '../../store/notificationStore'
import toast from 'react-hot-toast'

const PreferenceManager = () => {
  const { preferences, fetchPreferences, updatePreference, isLoading, error } = useNotificationStore()
  const [localPreferences, setLocalPreferences] = useState([])
  const [hasChanges, setHasChanges] = useState(false)

  useEffect(() => {
    fetchPreferences()
  }, [])

  useEffect(() => {
    setLocalPreferences([...preferences])
    setHasChanges(false)
  }, [preferences])

  const getChannelIcon = (channel) => {
    const icons = {
      email: Mail,
      sms: MessageSquare,
      push: Smartphone,
      webhook: Bell,
    }
    return icons[channel] || Bell
  }

  const getChannelColor = (channel) => {
    const colors = {
      email: 'text-blue-600 bg-blue-50 border-blue-200',
      sms: 'text-green-600 bg-green-50 border-green-200',
      push: 'text-purple-600 bg-purple-50 border-purple-200',
      webhook: 'text-orange-600 bg-orange-50 border-orange-200',
    }
    return colors[channel] || 'text-gray-600 bg-gray-50 border-gray-200'
  }

  const handlePreferenceChange = (prefId, field, value) => {
    setLocalPreferences(prev =>
      prev.map(pref =>
        pref.id === prefId
          ? { ...pref, [field]: value }
          : pref
      )
    )
    setHasChanges(true)
  }

  const handleTypeToggle = (prefId, type) => {
    setLocalPreferences(prev =>
      prev.map(pref => {
        if (pref.id === prefId) {
          const types = pref.types.includes(type)
            ? pref.types.filter(t => t !== type)
            : [...pref.types, type]
          return { ...pref, types }
        }
        return pref
      })
    )
    setHasChanges(true)
  }

  const handlePriorityToggle = (prefId, priority) => {
    setLocalPreferences(prev =>
      prev.map(pref => {
        if (pref.id === prefId) {
          const priorities = pref.priorities.includes(priority)
            ? pref.priorities.filter(p => p !== priority)
            : [...pref.priorities, priority]
          return { ...pref, priorities }
        }
        return pref
      })
    )
    setHasChanges(true)
  }

  const savePreferences = async () => {
    try {
      for (const pref of localPreferences) {
        await updatePreference(pref.id, {
          enabled: pref.enabled,
          types: pref.types,
          priorities: pref.priorities,
          settings: pref.settings
        })
      }
      setHasChanges(false)
      toast.success('Preferences saved successfully!')
    } catch (error) {
      toast.error('Failed to save preferences')
    }
  }

  const resetPreferences = () => {
    setLocalPreferences([...preferences])
    setHasChanges(false)
    toast.info('Changes reset')
  }

  const notificationTypes = ['success', 'error', 'warning', 'info']
  const priorityLevels = ['low', 'medium', 'high', 'critical']

  if (isLoading && preferences.length === 0) {
    return (
      <div className="p-6 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
        <p className="text-gray-500 mt-2">Loading preferences...</p>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center">
          <Settings className="w-5 h-5 mr-2" />
          Notification Preferences
        </h2>
        
        {hasChanges && (
          <div className="flex space-x-2">
            <button
              onClick={resetPreferences}
              className="flex items-center space-x-2 px-4 py-2 text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Reset</span>
            </button>
            <button
              onClick={savePreferences}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors"
            >
              <Save className="w-4 h-4" />
              <span>Save Changes</span>
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <div className="space-y-6">
        {localPreferences.map((preference) => {
          const Icon = getChannelIcon(preference.channel)
          const colorClass = getChannelColor(preference.channel)
          
          return (
            <div
              key={preference.id}
              className={`p-6 rounded-lg border-2 ${colorClass} transition-all duration-200`}
            >
              {/* Channel Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <Icon className="w-6 h-6" />
                  <div>
                    <h3 className="font-semibold text-lg capitalize">
                      {preference.channel}
                    </h3>
                    <p className="text-sm opacity-75">
                      Configure {preference.channel} notification settings
                    </p>
                  </div>
                </div>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={preference.enabled}
                    onChange={(e) => handlePreferenceChange(preference.id, 'enabled', e.target.checked)}
                    className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="font-medium">Enabled</span>
                </label>
              </div>

              {preference.enabled && (
                <>
                  {/* Notification Types */}
                  <div className="mb-4">
                    <h4 className="font-medium mb-2">Notification Types</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      {notificationTypes.map((type) => (
                        <label
                          key={type}
                          className="flex items-center space-x-2 p-2 rounded-lg border cursor-pointer hover:bg-white/50"
                        >
                          <input
                            type="checkbox"
                            checked={preference.types.includes(type)}
                            onChange={() => handleTypeToggle(preference.id, type)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <span className="capitalize text-sm">{type}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Priority Levels */}
                  <div>
                    <h4 className="font-medium mb-2">Priority Levels</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      {priorityLevels.map((priority) => (
                        <label
                          key={priority}
                          className="flex items-center space-x-2 p-2 rounded-lg border cursor-pointer hover:bg-white/50"
                        >
                          <input
                            type="checkbox"
                            checked={preference.priorities.includes(priority)}
                            onChange={() => handlePriorityToggle(preference.id, priority)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <span className="capitalize text-sm font-medium">{priority}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default PreferenceManager
