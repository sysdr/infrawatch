import React, { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, AreaChart, Area } from 'recharts'
import { Bell, CheckCircle, XCircle, AlertTriangle, TrendingUp, Activity, Users, Clock } from 'lucide-react'

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6']

// Demo data generator
const generateDemoData = () => {
  const now = new Date()
  const last24h = []
  for (let i = 23; i >= 0; i--) {
    last24h.push({
      hour: new Date(now.getTime() - i * 60 * 60 * 1000).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      alerts: Math.floor(Math.random() * 20) + 5,
      notifications: Math.floor(Math.random() * 50) + 10,
      success: Math.floor(Math.random() * 40) + 15
    })
  }

  return {
    stats: {
      totalNotifications: 1247,
      sent: 892,
      pending: 234,
      failed: 121,
      totalAlerts: 156,
      activeAlerts: 23,
      acknowledged: 89,
      resolved: 44
    },
    byStatus: [
      { name: 'SENT', value: 892 },
      { name: 'PENDING', value: 234 },
      { name: 'FAILED', value: 121 }
    ],
    byChannel: [
      { name: 'EMAIL', value: 456 },
      { name: 'SMS', value: 389 },
      { name: 'SLACK', value: 402 }
    ],
    bySeverity: [
      { name: 'CRITICAL', value: 12 },
      { name: 'HIGH', value: 45 },
      { name: 'MEDIUM', value: 67 },
      { name: 'LOW', value: 32 }
    ],
    timeline: last24h,
    recentAlerts: [
      { id: 1, service: 'API Gateway', severity: 'CRITICAL', status: 'NEW', message: 'High error rate detected', time: '2 min ago', escalation: 2 },
      { id: 2, service: 'Database', severity: 'HIGH', status: 'ACKNOWLEDGED', message: 'Connection pool exhausted', time: '5 min ago', escalation: 1 },
      { id: 3, service: 'Cache Service', severity: 'MEDIUM', status: 'NEW', message: 'Memory usage above threshold', time: '8 min ago', escalation: 0 },
      { id: 4, service: 'Payment API', severity: 'HIGH', status: 'NOTIFIED', message: 'Response time degraded', time: '12 min ago', escalation: 1 },
      { id: 5, service: 'Auth Service', severity: 'LOW', status: 'RESOLVED', message: 'Minor latency spike', time: '15 min ago', escalation: 0 }
    ],
    topServices: [
      { name: 'API Gateway', alerts: 45, notifications: 234 },
      { name: 'Database', alerts: 32, notifications: 189 },
      { name: 'Cache Service', alerts: 28, notifications: 156 },
      { name: 'Payment API', alerts: 24, notifications: 142 },
      { name: 'Auth Service', alerts: 18, notifications: 98 }
    ],
    notificationTrend: last24h.map(h => ({ time: h.hour, sent: h.success, failed: Math.floor(Math.random() * 10) }))
  }
}

function Dashboard() {
  const [data, setData] = useState(generateDemoData())
  const [isRealTime, setIsRealTime] = useState(true)

  useEffect(() => {
    if (!isRealTime) return

    const interval = setInterval(() => {
      // Simulate real-time updates
      setData(prevData => {
        const newData = { ...prevData }
        // Update stats slightly
        newData.stats.totalNotifications += Math.floor(Math.random() * 3)
        newData.stats.sent += Math.floor(Math.random() * 2)
        newData.stats.pending = Math.max(0, newData.stats.pending + Math.floor(Math.random() * 3) - 1)
        
        // Update timeline with new data point
        const now = new Date()
        const newPoint = {
          hour: now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
          alerts: Math.floor(Math.random() * 20) + 5,
          notifications: Math.floor(Math.random() * 50) + 10,
          success: Math.floor(Math.random() * 40) + 15
        }
        newData.timeline = [...newData.timeline.slice(1), newPoint]
        
        // Occasionally add new alert
        if (Math.random() > 0.7) {
          const services = ['API Gateway', 'Database', 'Cache Service', 'Payment API', 'Auth Service']
          const severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
          const statuses = ['NEW', 'ACKNOWLEDGED', 'NOTIFIED']
          const newAlert = {
            id: Date.now(),
            service: services[Math.floor(Math.random() * services.length)],
            severity: severities[Math.floor(Math.random() * severities.length)],
            status: statuses[Math.floor(Math.random() * statuses.length)],
            message: 'New alert detected',
            time: 'Just now',
            escalation: Math.floor(Math.random() * 3)
          }
          newData.recentAlerts = [newAlert, ...newData.recentAlerts.slice(0, 4)]
        }
        
        return newData
      })
    }, 3000) // Update every 3 seconds

    return () => clearInterval(interval)
  }, [isRealTime])

  const { stats, byStatus, byChannel, bySeverity, timeline, recentAlerts, topServices, notificationTrend } = data

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Notification Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">Real-time monitoring and metrics</p>
        </div>
        <div className="flex items-center space-x-4">
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={isRealTime}
              onChange={(e) => setIsRealTime(e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded"
            />
            <span className="text-sm text-gray-700">Real-time Updates</span>
          </label>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-600">Live</span>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={<Bell className="h-6 w-6 text-blue-600" />}
          title="Total Notifications"
          value={stats.totalNotifications.toLocaleString()}
          change="+12.5%"
          trend="up"
          bgColor="bg-blue-50"
        />
        <StatCard
          icon={<CheckCircle className="h-6 w-6 text-green-600" />}
          title="Success Rate"
          value={`${Math.round((stats.sent / stats.totalNotifications) * 100)}%`}
          change="+2.3%"
          trend="up"
          bgColor="bg-green-50"
        />
        <StatCard
          icon={<AlertTriangle className="h-6 w-6 text-orange-600" />}
          title="Active Alerts"
          value={stats.activeAlerts}
          change="-5"
          trend="down"
          bgColor="bg-orange-50"
        />
        <StatCard
          icon={<Activity className="h-6 w-6 text-purple-600" />}
          title="Avg Response Time"
          value="142ms"
          change="-8ms"
          trend="down"
          bgColor="bg-purple-50"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Notifications by Status */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center">
            <Bell className="h-5 w-5 mr-2 text-blue-600" />
            Notifications by Status
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={byStatus}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {byStatus.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Notifications by Channel */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center">
            <Activity className="h-5 w-5 mr-2 text-purple-600" />
            Notifications by Channel
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={byChannel}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Alerts by Severity */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center">
            <AlertTriangle className="h-5 w-5 mr-2 text-red-600" />
            Alerts by Severity
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={bySeverity}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#ef4444" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 24h Timeline */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
            24h Activity Timeline
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={timeline.slice(-12)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="alerts" stackId="1" stroke="#ef4444" fill="#fee2e2" />
              <Area type="monotone" dataKey="notifications" stackId="1" stroke="#3b82f6" fill="#dbeafe" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Notification Trend */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center">
          <Activity className="h-5 w-5 mr-2 text-blue-600" />
          Notification Success Trend (Last 24h)
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={notificationTrend.slice(-12)}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="sent" stroke="#10b981" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="failed" stroke="#ef4444" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Alerts */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center">
              <AlertTriangle className="h-5 w-5 mr-2 text-red-600" />
              Recent Alerts
            </h2>
            <span className="text-sm text-gray-500">{recentAlerts.length} active</span>
          </div>
          <div className="divide-y">
            {recentAlerts.map((alert) => (
              <div key={alert.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="font-semibold text-gray-900">{alert.service}</span>
                      <SeverityBadge severity={alert.severity} />
                      <StatusBadge status={alert.status} />
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{alert.message}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span className="flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {alert.time}
                      </span>
                      {alert.escalation > 0 && (
                        <span className="text-orange-600">Escalation Level {alert.escalation}</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Services */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold flex items-center">
              <Users className="h-5 w-5 mr-2 text-blue-600" />
              Top Services by Activity
            </h2>
          </div>
          <div className="p-6">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topServices} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={120} />
                <Tooltip />
                <Legend />
                <Bar dataKey="alerts" fill="#ef4444" name="Alerts" />
                <Bar dataKey="notifications" fill="#3b82f6" name="Notifications" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ icon, title, value, change, trend, bgColor }) {
  const isPositive = trend === 'up'
  return (
    <div className={`${bgColor} rounded-lg p-6 shadow-sm`}>
      <div className="flex items-center justify-between mb-4">
        {icon}
        {change && (
          <span className={`text-sm font-semibold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
            {isPositive ? '↑' : '↓'} {change}
          </span>
        )}
      </div>
      <div>
        <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
        <p className="text-3xl font-bold text-gray-900">{value}</p>
      </div>
    </div>
  )
}

function SeverityBadge({ severity }) {
  const colors = {
    CRITICAL: 'bg-red-100 text-red-800 border-red-200',
    HIGH: 'bg-orange-100 text-orange-800 border-orange-200',
    MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    LOW: 'bg-blue-100 text-blue-800 border-blue-200'
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

export default Dashboard
