import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { RefreshCw, Mail, MessageSquare, Smartphone, Webhook, Bell, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';

const COLORS = ['#4f46e5', '#059669', '#dc2626', '#ea580c', '#7c3aed'];

const Dashboard = ({ stats, notifications, onRefresh }) => {
  if (!stats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const channelData = Object.entries(stats.channels || {}).map(([name, data]) => ({
    name: name.toUpperCase(),
    sent: data.sent || 0,
    delivered: data.delivered || 0,
    failed: data.failed || 0
  }));

  const statusData = [
    { name: 'Delivered', value: stats.total_delivered, color: '#059669' },
    { name: 'Failed', value: stats.total_failed, color: '#dc2626' },
    { name: 'Pending', value: stats.total_notifications - stats.total_delivered - stats.total_failed, color: '#ea580c' }
  ];

  const channelIcons = {
    EMAIL: Mail,
    SMS: Smartphone,
    SLACK: MessageSquare,
    WEBHOOK: Webhook,
    PUSH: Bell
  };

  const recentNotifications = notifications.slice(0, 5);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-slate-900">Dashboard</h2>
        <button
          onClick={onRefresh}
          className="inline-flex items-center px-4 py-2 border border-slate-300 rounded-lg shadow-sm text-sm font-semibold text-slate-700 bg-white hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white overflow-hidden shadow-lg rounded-xl border border-slate-200 hover:shadow-xl transition-shadow duration-200">
          <div className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="bg-indigo-100 p-3 rounded-lg">
                  <Bell className="h-6 w-6 text-indigo-600" />
                </div>
              </div>
              <div className="ml-4 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-semibold text-slate-600 truncate">
                    Total Notifications
                  </dt>
                  <dd className="text-2xl font-bold text-slate-900">
                    {stats.total_notifications.toLocaleString()}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-lg rounded-xl border border-slate-200 hover:shadow-xl transition-shadow duration-200">
          <div className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="bg-emerald-100 p-3 rounded-lg">
                  <CheckCircle className="h-6 w-6 text-emerald-600" />
                </div>
              </div>
              <div className="ml-4 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-semibold text-slate-600 truncate">
                    Delivered
                  </dt>
                  <dd className="text-2xl font-bold text-slate-900">
                    {stats.total_delivered.toLocaleString()}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-lg rounded-xl border border-slate-200 hover:shadow-xl transition-shadow duration-200">
          <div className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="bg-red-100 p-3 rounded-lg">
                  <AlertCircle className="h-6 w-6 text-red-600" />
                </div>
              </div>
              <div className="ml-4 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-semibold text-slate-600 truncate">
                    Failed
                  </dt>
                  <dd className="text-2xl font-bold text-slate-900">
                    {stats.total_failed.toLocaleString()}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-lg rounded-xl border border-slate-200 hover:shadow-xl transition-shadow duration-200">
          <div className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="bg-purple-100 p-3 rounded-lg">
                  <TrendingUp className="h-6 w-6 text-purple-600" />
                </div>
              </div>
              <div className="ml-4 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-semibold text-slate-600 truncate">
                    Success Rate
                  </dt>
                  <dd className="text-2xl font-bold text-slate-900">
                    {stats.total_notifications > 0 
                      ? Math.round((stats.total_delivered / stats.total_notifications) * 100)
                      : 0}%
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Channel Performance Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Channel Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={channelData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="delivered" fill="#059669" name="Delivered" />
              <Bar dataKey="failed" fill="#dc2626" name="Failed" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Status Distribution */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Channel Status */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Channel Status</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {Object.entries(stats.channels || {}).map(([channel, data]) => {
              const Icon = channelIcons[channel.toUpperCase()] || Bell;
              const successRate = data.sent > 0 ? Math.round((data.delivered / data.sent) * 100) : 0;
              
              return (
                <div key={channel} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <Icon className="h-5 w-5 text-gray-600" />
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      successRate >= 95 ? 'bg-green-100 text-green-800' :
                      successRate >= 80 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {successRate}%
                    </span>
                  </div>
                  <h4 className="font-medium text-sm text-gray-900 mb-1">
                    {channel.toUpperCase()}
                  </h4>
                  <p className="text-xs text-gray-500">
                    {data.sent || 0} sent • {data.delivered || 0} delivered
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Recent Notifications */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Notifications</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {recentNotifications.map((notification) => {
            const Icon = channelIcons[notification.channel.toUpperCase()] || Bell;
            const statusColors = {
              delivered: 'text-green-600 bg-green-100',
              failed: 'text-red-600 bg-red-100',
              pending: 'text-yellow-600 bg-yellow-100',
              processing: 'text-blue-600 bg-blue-100'
            };
            
            return (
              <div key={notification.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Icon className="h-5 w-5 text-gray-400 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {notification.title}
                      </p>
                      <p className="text-sm text-gray-500">
                        {notification.recipient} • {notification.priority}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      statusColors[notification.status] || 'text-gray-600 bg-gray-100'
                    }`}>
                      {notification.status}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
