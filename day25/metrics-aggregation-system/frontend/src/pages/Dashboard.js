import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { Activity, TrendingUp, Database, Clock, AlertCircle, CheckCircle, Server, BarChart3 } from 'lucide-react';
import axios from 'axios';

const Dashboard = ({ isConnected, systemStats }) => {
  const [metrics, setMetrics] = useState([]);
  const [aggregationSummary, setSummary] = useState({});
  const [loading, setLoading] = useState(true);
  const [realTimeData, setRealTimeData] = useState([]);

  useEffect(() => {
    if (isConnected) {
      fetchDashboardData();
      setupWebSocket();
      
      // Refresh data every 30 seconds
      const interval = setInterval(fetchDashboardData, 30000);
      return () => clearInterval(interval);
    }
  }, [isConnected]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch current metrics
      const metricsResponse = await axios.get('/metrics/current');
      setMetrics(metricsResponse.data.data || []);
      
      // Fetch aggregation summary
      const summaryResponse = await axios.get('/metrics/summary');
      setSummary(summaryResponse.data.data || {});
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  const setupWebSocket = () => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'aggregated_metrics') {
          setRealTimeData(prev => {
            const newData = [...prev, {
              timestamp: new Date(data.timestamp).toLocaleTimeString(),
              ...data.data.reduce((acc, metric) => {
                if (metric.aggregations) {
                  acc[metric.metric_name] = metric.aggregations.average || 0;
                }
                return acc;
              }, {})
            }];
            
            // Keep only last 20 data points
            return newData.slice(-20);
          });
        }
      } catch (error) {
        console.error('WebSocket message error:', error);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
      // Attempt to reconnect after 5 seconds
      setTimeout(setupWebSocket, 5000);
    };

    return ws;
  };

  const StatCard = ({ title, value, icon: Icon, trend, color = "blue" }) => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className={`text-2xl font-bold text-${color}-600`}>{value}</p>
          {trend && (
            <p className={`text-sm ${trend > 0 ? 'text-green-600' : 'text-red-600'} flex items-center mt-1`}>
              <TrendingUp className="h-4 w-4 mr-1" />
              {trend > 0 ? '+' : ''}{trend}%
            </p>
          )}
        </div>
        <div className={`p-3 bg-${color}-100 rounded-lg`}>
          <Icon className={`h-6 w-6 text-${color}-600`} />
        </div>
      </div>
    </div>
  );

  const MetricChart = ({ data, title, dataKey, color = "#3B82F6" }) => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis dataKey="timestamp" stroke="#6B7280" fontSize={12} />
          <YAxis stroke="#6B7280" fontSize={12} />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'white', 
              border: '1px solid #E5E7EB', 
              borderRadius: '8px',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
            }} 
          />
          <Line 
            type="monotone" 
            dataKey={dataKey} 
            stroke={color} 
            strokeWidth={2}
            dot={{ fill: color, strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: color, strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading dashboard...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Metrics Aggregation Dashboard</h1>
          <p className="text-gray-600 mt-1">Real-time monitoring and analytics</p>
        </div>
        <div className="flex items-center space-x-2">
          {isConnected ? (
            <span className="flex items-center text-green-600">
              <CheckCircle className="h-5 w-5 mr-2" />
              Connected
            </span>
          ) : (
            <span className="flex items-center text-red-600">
              <AlertCircle className="h-5 w-5 mr-2" />
              Disconnected
            </span>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Active Windows"
          value={aggregationSummary.active_windows || 0}
          icon={Activity}
          color="blue"
        />
        <StatCard
          title="Total Metrics Processed"
          value={(aggregationSummary.total_metrics_processed || 0).toLocaleString()}
          icon={Database}
          trend={5.2}
          color="green"
        />
        <StatCard
          title="Real-time Data Points"
          value={realTimeData.length}
          icon={TrendingUp}
          color="purple"
        />
        <StatCard
          title="System Uptime"
          value="99.9%"
          icon={Server}
          color="indigo"
        />
      </div>

      {/* Real-time Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MetricChart
          data={realTimeData}
          title="CPU Usage Trends"
          dataKey="cpu_usage"
          color="#EF4444"
        />
        <MetricChart
          data={realTimeData}
          title="Memory Usage Trends"
          dataKey="memory_usage"
          color="#10B981"
        />
      </div>

      {/* Current Metrics Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Current Aggregated Metrics</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Metric Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Average
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Min / Max
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  P95
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Count
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {metrics.map((metric, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {metric.metric_name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {metric.window_key}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {metric.aggregations?.average?.toFixed(2) || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {metric.aggregations?.min?.toFixed(2) || 'N/A'} / {metric.aggregations?.max?.toFixed(2) || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {metric.aggregations?.p95?.toFixed(2) || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {metric.aggregations?.count || 0}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Components</h3>
          <div className="space-y-3">
            {Object.entries(systemStats.components || {}).map(([component, status]) => (
              <div key={component} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 capitalize">
                  {component.replace('_', ' ')}
                </span>
                <span className={`text-sm font-medium ${
                  status === 'running' || status === 'connected' 
                    ? 'text-green-600' 
                    : 'text-red-600'
                }`}>
                  {status}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Aggregation Latency</span>
              <span className="text-sm font-medium text-green-600">&lt; 100ms</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Memory Usage</span>
              <span className="text-sm font-medium text-blue-600">245 MB</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Storage Efficiency</span>
              <span className="text-sm font-medium text-purple-600">87%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Error Rate</span>
              <span className="text-sm font-medium text-green-600">0.01%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
