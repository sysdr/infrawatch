import React, { useState, useMemo } from 'react'
import { 
  Bell, 
  Check, 
  Filter, 
  Search, 
  AlertCircle, 
  CheckCircle, 
  AlertTriangle, 
  Info,
  X
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import useNotificationStore from '../../store/notificationStore'

const NotificationCenter = ({ onAcknowledge }) => {
  const { notifications, isLoading, error } = useNotificationStore()
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [filterPriority, setFilterPriority] = useState('all')
  const [showUnreadOnly, setShowUnreadOnly] = useState(false)

  const filteredNotifications = useMemo(() => {
    return notifications.filter(notification => {
      // Search filter
      const matchesSearch = searchTerm === '' || 
        notification.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        notification.message.toLowerCase().includes(searchTerm.toLowerCase())

      // Type filter
      const matchesType = filterType === 'all' || notification.type === filterType

      // Priority filter
      const matchesPriority = filterPriority === 'all' || notification.priority === filterPriority

      // Unread filter
      const matchesUnread = !showUnreadOnly || !notification.acknowledged

      return matchesSearch && matchesType && matchesPriority && matchesUnread
    })
  }, [notifications, searchTerm, filterType, filterPriority, showUnreadOnly])

  const getNotificationIcon = (type) => {
    const icons = {
      success: CheckCircle,
      error: AlertCircle,
      warning: AlertTriangle,
      info: Info,
    }
    return icons[type] || Info
  }

  const getNotificationColor = (type, priority) => {
    const typeColors = {
      success: 'text-green-600 bg-green-50 border-green-200',
      error: 'text-red-600 bg-red-50 border-red-200',
      warning: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      info: 'text-blue-600 bg-blue-50 border-blue-200',
    }
    
    if (priority === 'critical') {
      return 'text-red-600 bg-red-50 border-red-300 ring-2 ring-red-200'
    }
    
    return typeColors[type] || typeColors.info
  }

  const getPriorityBadge = (priority) => {
    const colors = {
      low: 'bg-gray-100 text-gray-800',
      medium: 'bg-blue-100 text-blue-800',
      high: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800',
    }
    
    return (
      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${colors[priority]}`}>
        {priority.toUpperCase()}
      </span>
    )
  }

  if (isLoading && notifications.length === 0) {
    return (
      <div className="p-6 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
        <p className="text-gray-500 mt-2">Loading notifications...</p>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center">
          <Bell className="w-5 h-5 mr-2" />
          Notifications ({filteredNotifications.length})
        </h2>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <div className="ml-3">
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="mb-6 space-y-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search notifications..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap gap-4">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Types</option>
            <option value="success">Success</option>
            <option value="error">Error</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
          </select>

          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>

          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={showUnreadOnly}
              onChange={(e) => setShowUnreadOnly(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Unread only</span>
          </label>
        </div>
      </div>

      {/* Notifications List */}
      <div className="space-y-3">
        {filteredNotifications.length === 0 ? (
          <div className="text-center py-12">
            <Bell className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900">No notifications</h3>
            <p className="text-gray-500">
              {searchTerm || filterType !== 'all' || filterPriority !== 'all' || showUnreadOnly
                ? 'No notifications match your current filters'
                : 'You\'re all caught up!'}
            </p>
          </div>
        ) : (
          filteredNotifications.map((notification) => {
            const Icon = getNotificationIcon(notification.type)
            const colorClass = getNotificationColor(notification.type, notification.priority)
            
            return (
              <div
                key={notification.id}
                className={`relative p-4 border rounded-lg transition-all duration-200 hover:shadow-md ${colorClass} ${
                  notification.acknowledged ? 'opacity-75' : ''
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    <Icon className="w-5 h-5 mt-0.5 flex-shrink-0" />
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <h4 className="font-medium text-gray-900 truncate">
                          {notification.title}
                        </h4>
                        {getPriorityBadge(notification.priority)}
                        {!notification.acknowledged && (
                          <span className="inline-flex w-2 h-2 bg-blue-500 rounded-full"></span>
                        )}
                      </div>
                      
                      <p className="text-gray-700 mb-2">{notification.message}</p>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-500">
                          {formatDistanceToNow(new Date(notification.timestamp), { addSuffix: true })}
                        </span>
                        
                        {!notification.acknowledged && (
                          <button
                            onClick={() => onAcknowledge(notification.id)}
                            className="flex items-center space-x-1 px-3 py-1 text-xs font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
                          >
                            <Check className="w-3 h-3" />
                            <span>Mark as read</span>
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}

export default NotificationCenter
