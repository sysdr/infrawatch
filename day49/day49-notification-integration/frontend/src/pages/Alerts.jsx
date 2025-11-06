import React, { useState, useEffect } from 'react'
import { Plus, CheckCircle, XCircle, AlertTriangle, Clock } from 'lucide-react'

// Demo data generator
const generateDemoAlerts = () => {
  const services = ['API Gateway', 'Database', 'Cache Service', 'Payment API', 'Auth Service', 'Message Queue', 'File Storage', 'Search Service']
  const alertTypes = ['CPU', 'Memory', 'Disk', 'Network', 'Error Rate', 'Latency', 'Throughput']
  const severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
  const statuses = ['NEW', 'NOTIFIED', 'ACKNOWLEDGED', 'RESOLVED']
  const messages = [
    'High error rate detected',
    'Connection pool exhausted',
    'Memory usage above threshold',
    'Response time degraded',
    'Disk space running low',
    'Network latency spike',
    'Service unavailable',
    'Timeout errors increasing'
  ]

  return Array.from({ length: 25 }, (_, i) => {
    const created = new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000)
    const severity = severities[Math.floor(Math.random() * severities.length)]
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    
    return {
      id: i + 1,
      service_name: services[Math.floor(Math.random() * services.length)],
      alert_type: alertTypes[Math.floor(Math.random() * alertTypes.length)],
      severity: severity,
      status: status,
      message: messages[Math.floor(Math.random() * messages.length)],
      created_at: created.toISOString(),
      acknowledged_by: status === 'ACKNOWLEDGED' ? `user${Math.floor(Math.random() * 5) + 1}` : null,
      escalation_level: severity === 'CRITICAL' ? 2 : severity === 'HIGH' ? 1 : 0
    }
  }).sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
}

function Alerts() {
  const [alerts, setAlerts] = useState([])
  const [showCreate, setShowCreate] = useState(false)
  const [filterStatus, setFilterStatus] = useState('ALL')

  useEffect(() => {
    // Load demo data
    setAlerts(generateDemoAlerts())
  }, [])

  const handleCreateAlert = async (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    
    const newAlert = {
      id: Date.now(),
      service_name: formData.get('service_name'),
      alert_type: formData.get('alert_type'),
      severity: formData.get('severity'),
      status: 'NEW',
      message: formData.get('message'),
      created_at: new Date().toISOString(),
      acknowledged_by: null,
      escalation_level: formData.get('severity') === 'CRITICAL' ? 2 : formData.get('severity') === 'HIGH' ? 1 : 0
    }
    
    setAlerts([newAlert, ...alerts])
    setShowCreate(false)
    e.target.reset()
    alert('Alert created successfully!')
  }

  const handleAcknowledge = async (alertId) => {
    setAlerts(alerts.map(alert => 
      alert.id === alertId 
        ? { ...alert, status: 'ACKNOWLEDGED', acknowledged_by: 'user1', acknowledged_at: new Date().toISOString() }
        : alert
    ))
    alert('Alert acknowledged!')
  }

  const handleResolve = async (alertId) => {
    setAlerts(alerts.map(alert => 
      alert.id === alertId 
        ? { ...alert, status: 'RESOLVED', resolved_at: new Date().toISOString() }
        : alert
    ))
    alert('Alert resolved!')
  }

  const filteredAlerts = filterStatus === 'ALL' 
    ? alerts 
    : alerts.filter(a => a.status === filterStatus)

  const stats = {
    total: alerts.length,
    new: alerts.filter(a => a.status === 'NEW').length,
    acknowledged: alerts.filter(a => a.status === 'ACKNOWLEDGED').length,
    resolved: alerts.filter(a => a.status === 'RESOLVED').length
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Alerts</h1>
          <p className="text-sm text-gray-500 mt-1">Monitor and manage system alerts</p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          Create Alert
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Total Alerts</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{stats.total}</div>
        </div>
        <div className="bg-yellow-50 rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">New</div>
          <div className="text-2xl font-bold text-yellow-600 mt-1">{stats.new}</div>
        </div>
        <div className="bg-blue-50 rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Acknowledged</div>
          <div className="text-2xl font-bold text-blue-600 mt-1">{stats.acknowledged}</div>
        </div>
        <div className="bg-green-50 rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Resolved</div>
          <div className="text-2xl font-bold text-green-600 mt-1">{stats.resolved}</div>
        </div>
      </div>

      {/* Filter */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700">Filter by Status:</span>
          {['ALL', 'NEW', 'ACKNOWLEDGED', 'RESOLVED'].map(status => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filterStatus === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {showCreate && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Create New Alert</h2>
          <form onSubmit={handleCreateAlert} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Service Name
                </label>
                <input
                  type="text"
                  name="service_name"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., API Gateway"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Alert Type
                </label>
                <input
                  type="text"
                  name="alert_type"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., CPU, Memory"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Severity
                </label>
                <select
                  name="severity"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                  <option value="CRITICAL">Critical</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Message
                </label>
                <input
                  type="text"
                  name="message"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Alert description"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowCreate(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create Alert
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Service
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Severity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Message
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredAlerts.length > 0 ? (
                filteredAlerts.map((alert) => (
                  <tr key={alert.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {alert.service_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {alert.alert_type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <SeverityBadge severity={alert.severity} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge status={alert.status} />
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                      {alert.message}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {new Date(alert.created_at).toLocaleString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex items-center space-x-2">
                        {alert.status !== 'ACKNOWLEDGED' && alert.status !== 'RESOLVED' && (
                          <button
                            onClick={() => handleAcknowledge(alert.id)}
                            className="text-blue-600 hover:text-blue-900 flex items-center"
                            title="Acknowledge"
                          >
                            <CheckCircle className="h-4 w-4" />
                          </button>
                        )}
                        {alert.status !== 'RESOLVED' && (
                          <button
                            onClick={() => handleResolve(alert.id)}
                            className="text-green-600 hover:text-green-900 flex items-center"
                            title="Resolve"
                          >
                            <XCircle className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" className="px-6 py-8 text-center text-gray-500">
                    No alerts found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function SeverityBadge({ severity }) {
  const colors = {
    LOW: 'bg-blue-100 text-blue-800 border-blue-200',
    MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    HIGH: 'bg-orange-100 text-orange-800 border-orange-200',
    CRITICAL: 'bg-red-100 text-red-800 border-red-200'
  }
  return (
    <span className={`px-2 py-1 text-xs font-semibold rounded border ${colors[severity] || colors.LOW}`}>
      {severity}
    </span>
  )
}

function StatusBadge({ status }) {
  const colors = {
    NEW: 'bg-gray-100 text-gray-800',
    NOTIFIED: 'bg-blue-100 text-blue-800',
    ACKNOWLEDGED: 'bg-green-100 text-green-800',
    ESCALATED: 'bg-orange-100 text-orange-800',
    RESOLVED: 'bg-green-100 text-green-800'
  }
  return (
    <span className={`px-2 py-1 text-xs font-semibold rounded ${colors[status] || colors.NEW}`}>
      {status}
    </span>
  )
}

export default Alerts
