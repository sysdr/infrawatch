import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, TrendingDown, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

const Dashboard = ({ realtimeData }) => {
  const [metrics, setMetrics] = useState(null);
  const [realtimeMetrics, setRealtimeMetrics] = useState(null);

  useEffect(() => {
    fetchDashboardMetrics();
    fetchRealtimeMetrics();
    
    const interval = setInterval(fetchRealtimeMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardMetrics = async () => {
    try {
      const response = await fetch('/api/metrics/dashboard');
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Failed to fetch dashboard metrics:', error);
    }
  };

  const fetchRealtimeMetrics = async () => {
    try {
      const response = await fetch('/api/metrics/real-time');
      const data = await response.json();
      setRealtimeMetrics(data);
    } catch (error) {
      console.error('Failed to fetch realtime metrics:', error);
    }
  };

  if (!metrics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'];

  const channelData = Object.entries(metrics.channel_breakdown).map(([channel, data]) => ({
    name: channel.toUpperCase(),
    value: data.count,
    success_rate: data.success_rate.toFixed(1)
  }));

  return (
    <div className="space-y-6">
      {/* Real-time Alert */}
      {realtimeData && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertCircle className="h-5 w-5 text-blue-600" />
            <span className="text-sm font-medium text-blue-800">
              Real-time Update: {realtimeData.type} - {realtimeData.notification?.channel} notification {realtimeData.result?.status}
            </span>
          </div>
        </div>
      )}

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Notifications</p>
              <p className="text-3xl font-bold text-gray-900">{metrics.overview.total_notifications.toLocaleString()}</p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-3xl font-bold text-green-600">{metrics.overview.success_rate.toFixed(1)}%</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Delivery Time</p>
              <p className="text-3xl font-bold text-blue-600">{Math.round(metrics.overview.avg_delivery_time)}ms</p>
            </div>
            <Clock className="h-8 w-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Queue Size</p>
              <p className="text-3xl font-bold text-orange-600">{metrics.overview.current_queue_size}</p>
            </div>
            <AlertCircle className="h-8 w-8 text-orange-500" />
          </div>
        </div>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hourly Stats */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Hourly Delivery Stats</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={metrics.hourly_stats}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="sent" fill="#3B82F6" />
              <Bar dataKey="delivered" fill="#10B981" />
              <Bar dataKey="failed" fill="#EF4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Channel Breakdown */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Channel Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={channelData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({name, value}) => `${name}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {channelData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Real-time Data */}
      {realtimeMetrics && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Real-time Events */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Real-time Events</h3>
            <div className="space-y-3">
              {realtimeMetrics.recent_events.map((event, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${
                      event.type === 'delivery_success' ? 'bg-green-500' :
                      event.type === 'delivery_failed' ? 'bg-red-500' :
                      event.type === 'queued' ? 'bg-blue-500' : 'bg-yellow-500'
                    }`}></div>
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {event.type.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold text-gray-900">{event.count}</div>
                    <div className="text-xs text-gray-500">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* System Status */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-600">Processing Rate</span>
                <span className="text-sm font-bold text-gray-900">
                  {realtimeMetrics.processing_rate.toFixed(1)} msg/sec
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-600">Active Workers</span>
                <span className="text-sm font-bold text-gray-900">{realtimeMetrics.active_workers}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-600">Memory Usage</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full" 
                      style={{width: `${realtimeMetrics.memory_usage}%`}}
                    ></div>
                  </div>
                  <span className="text-sm font-bold text-gray-900">
                    {Math.round(realtimeMetrics.memory_usage)}%
                  </span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-600">CPU Usage</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full" 
                      style={{width: `${realtimeMetrics.cpu_usage}%`}}
                    ></div>
                  </div>
                  <span className="text-sm font-bold text-gray-900">
                    {Math.round(realtimeMetrics.cpu_usage)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Priority Stats */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Priority Distribution</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(metrics.priority_stats).map(([priority, data]) => (
            <div key={priority} className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">{data.count.toLocaleString()}</div>
              <div className="text-sm font-medium text-gray-600 capitalize">{priority}</div>
              <div className="text-xs text-gray-500 mt-1">
                Avg: {Math.round(data.avg_time)}ms
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
