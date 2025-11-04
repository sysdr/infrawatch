import React, { useState, useEffect, useMemo } from 'react'
import { History, Search, Filter, Calendar, Download, X } from 'lucide-react'
import { formatDistanceToNow, format } from 'date-fns'
import useNotificationStore from '../../store/notificationStore'

const NotificationHistory = () => {
  const { history, fetchHistory, isLoading, error } = useNotificationStore()
  const [searchTerm, setSearchTerm] = useState('')
  const [actionFilter, setActionFilter] = useState('all')
  const [dateRange, setDateRange] = useState('all')
  const [selectedNotification, setSelectedNotification] = useState(null)

  useEffect(() => {
    fetchHistory()
  }, [])

  const filteredHistory = useMemo(() => {
    let filtered = history

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(item =>
        item.notificationId.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (item.details && JSON.stringify(item.details).toLowerCase().includes(searchTerm.toLowerCase()))
      )
    }

    // Action filter
    if (actionFilter !== 'all') {
      filtered = filtered.filter(item => item.action === actionFilter)
    }

    // Date range filter
    if (dateRange !== 'all') {
      const now = new Date()
      let cutoffDate

      switch (dateRange) {
        case 'today':
          cutoffDate = new Date(now.setHours(0, 0, 0, 0))
          break
        case 'week':
          cutoffDate = new Date(now.setDate(now.getDate() - 7))
          break
        case 'month':
          cutoffDate = new Date(now.setMonth(now.getMonth() - 1))
          break
        default:
          cutoffDate = null
      }

      if (cutoffDate) {
        filtered = filtered.filter(item => new Date(item.timestamp) >= cutoffDate)
      }
    }

    return filtered
  }, [history, searchTerm, actionFilter, dateRange])

  const getActionIcon = (action) => {
    const icons = {
      created: '🟢',
      sent: '📤',
      delivered: '✅',
      acknowledged: '👀',
      failed: '❌',
      expired: '⏰',
      archived: '📁'
    }
    return icons[action] || '📋'
  }

  const getActionColor = (action) => {
    const colors = {
      created: 'bg-blue-50 text-blue-700 border-blue-200',
      sent: 'bg-yellow-50 text-yellow-700 border-yellow-200',
      delivered: 'bg-green-50 text-green-700 border-green-200',
      acknowledged: 'bg-purple-50 text-purple-700 border-purple-200',
      failed: 'bg-red-50 text-red-700 border-red-200',
      expired: 'bg-gray-50 text-gray-700 border-gray-200',
      archived: 'bg-indigo-50 text-indigo-700 border-indigo-200'
    }
    return colors[action] || 'bg-gray-50 text-gray-700 border-gray-200'
  }

  const exportHistory = () => {
    const exportData = filteredHistory.map(item => ({
      timestamp: format(new Date(item.timestamp), 'yyyy-MM-dd HH:mm:ss'),
      notificationId: item.notificationId,
      action: item.action,
      details: JSON.stringify(item.details || {})
    }))

    const csv = [
      ['Timestamp', 'Notification ID', 'Action', 'Details'],
      ...exportData.map(row => [row.timestamp, row.notificationId, row.action, row.details])
    ].map(row => row.join(',')).join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `notification-history-${format(new Date(), 'yyyy-MM-dd')}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const uniqueActions = [...new Set(history.map(item => item.action))]

  if (isLoading && history.length === 0) {
    return (
      <div className="p-6 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
        <p className="text-gray-500 mt-2">Loading history...</p>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center">
          <History className="w-5 h-5 mr-2" />
          Notification History ({filteredHistory.length})
        </h2>
        
        <button
          onClick={exportHistory}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors"
        >
          <Download className="w-4 h-4" />
          <span>Export CSV</span>
        </button>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Filters */}
      <div className="mb-6 space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search history..."
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

        <div className="flex flex-wrap gap-4">
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Actions</option>
            {uniqueActions.map(action => (
              <option key={action} value={action}>
                {action.charAt(0).toUpperCase() + action.slice(1)}
              </option>
            ))}
          </select>

          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Time</option>
            <option value="today">Today</option>
            <option value="week">Last Week</option>
            <option value="month">Last Month</option>
          </select>
        </div>
      </div>

      {/* History Timeline */}
      <div className="space-y-4">
        {filteredHistory.length === 0 ? (
          <div className="text-center py-12">
            <History className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900">No history found</h3>
            <p className="text-gray-500">
              {searchTerm || actionFilter !== 'all' || dateRange !== 'all'
                ? 'No history matches your current filters'
                : 'No notification history available'}
            </p>
          </div>
        ) : (
          filteredHistory.map((item, index) => {
            const colorClass = getActionColor(item.action)
            const isLast = index === filteredHistory.length - 1
            
            return (
              <div key={item.id} className="relative">
                {/* Timeline line */}
                {!isLast && (
                  <div className="absolute left-4 top-16 bottom-0 w-0.5 bg-gray-200" />
                )}
                
                <div className="flex items-start space-x-4">
                  {/* Timeline dot */}
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full border-2 flex items-center justify-center text-xs ${colorClass}`}>
                    {getActionIcon(item.action)}
                  </div>
                  
                  {/* Content */}
                  <div className="flex-1 min-w-0 pb-8">
                    <div className={`p-4 rounded-lg border ${colorClass.replace('text-', 'text-').replace('border-', 'border-')}`}>
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium capitalize">{item.action}</span>
                          <span className="text-xs px-2 py-1 bg-white/50 rounded">
                            ID: {item.notificationId.slice(-8)}
                          </span>
                        </div>
                        <span className="text-xs opacity-75">
                          {formatDistanceToNow(new Date(item.timestamp), { addSuffix: true })}
                        </span>
                      </div>
                      
                      <div className="text-sm opacity-90">
                        <span className="font-medium">Time:</span>{' '}
                        {format(new Date(item.timestamp), 'MMM dd, yyyy HH:mm:ss')}
                      </div>
                      
                      {item.details && Object.keys(item.details).length > 0 && (
                        <div className="mt-2 text-xs">
                          <button
                            onClick={() => setSelectedNotification(
                              selectedNotification === item.id ? null : item.id
                            )}
                            className="text-blue-600 hover:text-blue-800 underline"
                          >
                            {selectedNotification === item.id ? 'Hide details' : 'Show details'}
                          </button>
                          
                          {selectedNotification === item.id && (
                            <div className="mt-2 p-2 bg-white/30 rounded text-xs font-mono">
                              <pre>{JSON.stringify(item.details, null, 2)}</pre>
                            </div>
                          )}
                        </div>
                      )}
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

export default NotificationHistory
