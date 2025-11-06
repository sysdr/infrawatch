import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Save } from 'lucide-react'

function Preferences() {
  const [userId, setUserId] = useState('user1')
  const [preferences, setPreferences] = useState({
    email: '',
    phone: '',
    slack_id: '',
    preferences: {
      LOW: { channels: ['EMAIL'] },
      MEDIUM: { channels: ['EMAIL'] },
      HIGH: { channels: ['EMAIL', 'SLACK'] },
      CRITICAL: { channels: ['EMAIL', 'SMS', 'SLACK'] }
    }
  })
  const [saved, setSaved] = useState(false)
  
  useEffect(() => {
    loadPreferences()
  }, [userId])
  
  const loadPreferences = async () => {
    try {
      const res = await axios.get(`/api/preferences/${userId}`)
      setPreferences(res.data)
    } catch (error) {
      console.log('No existing preferences, using defaults')
    }
  }
  
  const handleSave = async (e) => {
    e.preventDefault()
    try {
      await axios.post(`/api/preferences/${userId}`, preferences)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (error) {
      console.error('Error saving preferences:', error)
    }
  }
  
  const toggleChannel = (severity, channel) => {
    const currentChannels = preferences.preferences[severity]?.channels || []
    const newChannels = currentChannels.includes(channel)
      ? currentChannels.filter(c => c !== channel)
      : [...currentChannels, channel]
    
    setPreferences({
      ...preferences,
      preferences: {
        ...preferences.preferences,
        [severity]: { channels: newChannels }
      }
    })
  }
  
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Notification Preferences</h1>
      
      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSave} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              User ID
            </label>
            <input
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={preferences.email}
                onChange={(e) => setPreferences({ ...preferences, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="user@example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone (SMS)
              </label>
              <input
                type="tel"
                value={preferences.phone || ''}
                onChange={(e) => setPreferences({ ...preferences, phone: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="+1234567890"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Slack ID
              </label>
              <input
                type="text"
                value={preferences.slack_id || ''}
                onChange={(e) => setPreferences({ ...preferences, slack_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="U12345678"
              />
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-4">Channel Preferences by Severity</h3>
            <div className="space-y-4">
              {['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map((severity) => (
                <div key={severity} className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium mb-3 text-gray-900">{severity}</h4>
                  <div className="flex space-x-6">
                    {['EMAIL', 'SMS', 'SLACK'].map((channel) => (
                      <label key={channel} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={preferences.preferences[severity]?.channels?.includes(channel) || false}
                          onChange={() => toggleChannel(severity, channel)}
                          className="w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <span className="text-sm text-gray-700">{channel}</span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <button
              type="submit"
              className="flex items-center px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Save className="h-5 w-5 mr-2" />
              Save Preferences
            </button>
            {saved && (
              <span className="text-green-600 font-medium">✓ Preferences saved successfully!</span>
            )}
          </div>
        </form>
      </div>
    </div>
  )
}

export default Preferences
