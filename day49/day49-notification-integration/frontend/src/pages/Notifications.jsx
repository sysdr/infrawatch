import React, { useState, useEffect } from 'react'
import { Bell, Mail, MessageSquare, CheckCircle, XCircle, Clock, Filter } from 'lucide-react'

// Demo data generator
const generateDemoNotifications = () => {
  const channels = ['EMAIL', 'SMS', 'SLACK']
  const statuses = ['PENDING', 'SENT', 'DELIVERED', 'FAILED']
  const users = ['user1', 'user2', 'user3', 'user4', 'user5']
  const messages = [
    'Alert: High CPU usage detected',
    'Service degradation in API Gateway',
    'Database connection pool exhausted',
    'Memory usage above threshold',
    'Network latency spike detected',
    'Disk space running low',
    'Error rate increased significantly',
    'Service timeout errors'
  ]

  return Array.from({ length: 50 }, (_, i) => {
    const created = new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000)
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    const channel = channels[Math.floor(Math.random() * channels.length)]
    
    return {
      id: i + 1,
      alert_id: Math.floor(Math.random() * 25) + 1,
      user_id: users[Math.floor(Math.random() * users.length)],
      channel: channel,
      status: status,
      message: messages[Math.floor(Math.random() * messages.length)],
      sent_at: status !== 'PENDING' ? new Date(created.getTime() + Math.random() * 60000).toISOString() : null,
      delivered_at: status === 'DELIVERED' ? new Date(created.getTime() + Math.random() * 120000).toISOString() : null,
      failed_reason: status === 'FAILED' ? 'Network timeout' : null,
      retry_count: status === 'FAILED' ? Math.floor(Math.random() * 3) : 0,
      created_at: created.toISOString()
    }
  }).sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
}

function Notifications() {
  const [notifications, setNotifications] = useState([])
  const [filterChannel, setFilterChannel] = useState('ALL')
  const [filterStatus, setFilterStatus] = useState('ALL')
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    // Load demo data
    setNotifications(generateDemoNotifications())
  }, [])

  const filteredNotifications = notifications.filter(n => {
    const matchesChannel = filterChannel === 'ALL' || n.channel === filterChannel
    const matchesStatus = filterStatus === 'ALL' || n.status === filterStatus
    const matchesSearch = searchTerm === '' || 
      n.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      n.user_id.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesChannel && matchesStatus && matchesSearch
  })

  const stats = {
    total: notifications.length,
    sent: notifications.filter(n => n.status === 'SENT' || n.status === 'DELIVERED').length,
    pending: notifications.filter(n => n.status === 'PENDING').length,
    failed: notifications.filter(n => n.status === 'FAILED').length,
    byChannel: {
      EMAIL: notifications.filter(n => n.channel === 'EMAIL').length,
      SMS: notifications.filter(n => n.channel === 'SMS').length,
      SLACK: notifications.filter(n => n.channel === 'SLACK').length
    }
  }

  const getChannelIcon = (channel) => {
    switch(channel) {
      case 'EMAIL': return <Mail className="h-4 w-4" />
      case 'SMS': return <MessageSquare className="h-4 w-4" />
      case 'SLACK': return <Bell className="h-4 w-4" />
      default: return <Bell className="h-4 w-4" />
    }
  }

  const getChannelColor = (channel) => {
    switch(channel) {
      case 'EMAIL': return 'bg-blue-100 text-blue-800'
      case 'SMS': return 'bg-green-100 text-green-800'
      case 'SLACK': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Notifications</h1>
          <p className="text-sm text-gray-500 mt-1">Monitor notification delivery and status</p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Total Notifications</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{stats.total}</div>
        </div>
        <div className="bg-green-50 rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Sent/Delivered</div>
          <div className="text-2xl font-bold text-green-600 mt-1">{stats.sent}</div>
        </div>
        <div className="bg-yellow-50 rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Pending</div>
          <div className="text-2xl font-bold text-yellow-600 mt-1">{stats.pending}</div>
        </div>
        <div className="bg-red-50 rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Failed</div>
          <div className="text-2xl font-bold text-red-600 mt-1">{stats.failed}</div>
        </div>
      </div>

      {/* Channel Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-600">Email</div>
              <div className="text-2xl font-bold text-blue-600 mt-1">{stats.byChannel.EMAIL}</div>
            </div>
            <Mail className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        <div className="bg-green-50 rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-600">SMS</div>
              <div className="text-2xl font-bold text-green-600 mt-1">{stats.byChannel.SMS}</div>
            </div>
            <MessageSquare className="h-8 w-8 text-green-600" />
          </div>
        </div>
        <div className="bg-purple-50 rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-600">Slack</div>
              <div className="text-2xl font-bold text-purple-600 mt-1">{stats.byChannel.SLACK}</div>
            </div>
            <Bell className="h-8 w-8 text-purple-600" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0 md:space-x-4">
          <div className="flex items-center space-x-4">
            <Filter className="h-5 w-5 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Filter by Channel:</span>
            {['ALL', 'EMAIL', 'SMS', 'SLACK'].map(channel => (
              <button
                key={channel}
                onClick={() => setFilterChannel(channel)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filterChannel === channel
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {channel}
              </button>
            ))}
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-700">Filter by Status:</span>
            {['ALL', 'PENDING', 'SENT', 'DELIVERED', 'FAILED'].map(status => (
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
        <div className="mt-4">
          <input
            type="text"
            placeholder="Search by message or user..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Notifications Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Channel
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Message
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Alert ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Retries
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredNotifications.length > 0 ? (
                filteredNotifications.map((notification) => (
                  <tr key={notification.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      #{notification.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs font-semibold rounded flex items-center space-x-1 ${getChannelColor(notification.channel)}`}>
                          {getChannelIcon(notification.channel)}
                          <span>{notification.channel}</span>
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {notification.user_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge status={notification.status} />
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                      {notification.message}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      #{notification.alert_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {new Date(notification.created_at).toLocaleString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {notification.retry_count > 0 ? (
                        <span className="text-orange-600 font-medium">{notification.retry_count}</span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8" className="px-6 py-8 text-center text-gray-500">
                    No notifications found
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

function StatusBadge({ status }) {
  const colors = {
    PENDING: 'bg-yellow-100 text-yellow-800',
    SENT: 'bg-blue-100 text-blue-800',
    DELIVERED: 'bg-green-100 text-green-800',
    FAILED: 'bg-red-100 text-red-800'
  }
  
  const icons = {
    PENDING: <Clock className="h-3 w-3" />,
    SENT: <Bell className="h-3 w-3" />,
    DELIVERED: <CheckCircle className="h-3 w-3" />,
    FAILED: <XCircle className="h-3 w-3" />
  }

  return (
    <span className={`px-2 py-1 text-xs font-semibold rounded flex items-center space-x-1 w-fit ${colors[status] || colors.PENDING}`}>
      {icons[status]}
      <span>{status}</span>
    </span>
  )
}

export default Notifications
