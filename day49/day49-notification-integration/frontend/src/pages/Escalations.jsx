import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Plus } from 'lucide-react'

function Escalations() {
  const [policies, setPolicies] = useState([])
  const [showCreate, setShowCreate] = useState(false)
  
  useEffect(() => {
    loadPolicies()
  }, [])
  
  const loadPolicies = async () => {
    try {
      const res = await axios.get('/api/escalations/')
      setPolicies(res.data)
    } catch (error) {
      console.error('Error loading policies:', error)
    }
  }
  
  const handleCreate = async (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    
    const policy = {
      service_name: formData.get('service_name'),
      severity: formData.get('severity'),
      policy_config: [
        {
          level: 0,
          users: formData.get('level0_users').split(',').map(u => u.trim()),
          timeout_minutes: parseInt(formData.get('level0_timeout'))
        },
        {
          level: 1,
          users: formData.get('level1_users').split(',').map(u => u.trim()),
          timeout_minutes: parseInt(formData.get('level1_timeout'))
        }
      ]
    }
    
    try {
      await axios.post('/api/escalations/', policy)
      setShowCreate(false)
      e.target.reset()
      loadPolicies()
    } catch (error) {
      console.error('Error creating policy:', error)
    }
  }
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Escalation Policies</h1>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="h-5 w-5 mr-2" />
          Create Policy
        </button>
      </div>
      
      {showCreate && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Create Escalation Policy</h2>
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Service Name
                </label>
                <input
                  type="text"
                  name="service_name"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="api-gateway"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Severity
                </label>
                <select
                  name="severity"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="HIGH">High</option>
                  <option value="CRITICAL">Critical</option>
                </select>
              </div>
            </div>
            
            <div className="border-t pt-4">
              <h3 className="font-medium mb-3">Level 0 (On-Call)</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Users (comma-separated)
                  </label>
                  <input
                    type="text"
                    name="level0_users"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="user1, user2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Timeout (minutes)
                  </label>
                  <input
                    type="number"
                    name="level0_timeout"
                    required
                    defaultValue="5"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
            </div>
            
            <div className="border-t pt-4">
              <h3 className="font-medium mb-3">Level 1 (Team Lead)</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Users (comma-separated)
                  </label>
                  <input
                    type="text"
                    name="level1_users"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="manager1, manager2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Timeout (minutes)
                  </label>
                  <input
                    type="number"
                    name="level1_timeout"
                    required
                    defaultValue="10"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowCreate(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Create Policy
              </button>
            </div>
          </form>
        </div>
      )}
      
      <div className="space-y-4">
        {policies.map((policy) => (
          <div key={policy.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">{policy.service_name}</h3>
              <span className={`px-3 py-1 text-sm font-semibold rounded ${
                policy.severity === 'CRITICAL' ? 'bg-red-100 text-red-800' : 'bg-orange-100 text-orange-800'
              }`}>
                {policy.severity}
              </span>
            </div>
            <div className="space-y-3">
              {policy.policy_config.map((level, idx) => (
                <div key={idx} className="border-l-4 border-blue-500 pl-4 py-2">
                  <div className="font-medium text-gray-900">Level {level.level}</div>
                  <div className="text-sm text-gray-600">
                    Users: {level.users.join(', ')}
                  </div>
                  <div className="text-sm text-gray-600">
                    Timeout: {level.timeout_minutes} minutes
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Escalations
