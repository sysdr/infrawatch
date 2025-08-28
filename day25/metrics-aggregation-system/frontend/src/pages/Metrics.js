import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import axios from 'axios';

const Metrics = ({ isConnected }) => {
  const [currentMetrics, setCurrentMetrics] = useState([]);
  const [trends, setTrends] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedMetric, setSelectedMetric] = useState(null);

  useEffect(() => {
    if (isConnected) {
      fetchMetrics();
      const interval = setInterval(fetchMetrics, 5000);
      return () => clearInterval(interval);
    }
  }, [isConnected]);

  const fetchMetrics = async () => {
    try {
      const response = await axios.get('/metrics/current');
      setCurrentMetrics(response.data.data || []);
      
      // Fetch trends for first metric if available
      if (response.data.data && response.data.data.length > 0) {
        const firstMetric = response.data.data[0];
        fetchTrends(firstMetric.metric_name);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching metrics:', error);
      setLoading(false);
    }
  };

  const fetchTrends = async (metricName) => {
    try {
      const response = await axios.get(`/metrics/trends/${metricName}`);
      setTrends(response.data.trends || {});
    } catch (error) {
      console.error('Error fetching trends:', error);
    }
  };

  const getTrendIcon = (changePercent) => {
    if (changePercent > 5) return <TrendingUp className="h-4 w-4 text-green-600" />;
    if (changePercent < -5) return <TrendingDown className="h-4 w-4 text-red-600" />;
    return <Minus className="h-4 w-4 text-gray-600" />;
  };

  const MetricCard = ({ metric }) => {
    const agg = metric.aggregations || {};
    
    return (
      <div 
        className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 cursor-pointer hover:shadow-md transition-shadow"
        onClick={() => setSelectedMetric(metric)}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 capitalize">
            {metric.metric_name.replace('_', ' ')}
          </h3>
          <Activity className="h-5 w-5 text-blue-600" />
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Current Average</p>
            <p className="text-2xl font-bold text-blue-600">
              {agg.average ? agg.average.toFixed(2) : 'N/A'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Data Points</p>
            <p className="text-2xl font-bold text-gray-900">
              {agg.count || 0}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Min / Max</p>
            <p className="text-sm font-medium text-gray-700">
              {agg.min ? agg.min.toFixed(2) : 'N/A'} / {agg.max ? agg.max.toFixed(2) : 'N/A'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">P95</p>
            <p className="text-sm font-medium text-gray-700">
              {agg.p95 ? agg.p95.toFixed(2) : 'N/A'}
            </p>
          </div>
        </div>
        
        {trends[metric.window_key] && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Trend</span>
              <div className="flex items-center">
                {getTrendIcon(trends[metric.window_key].change_percent)}
                <span className={`ml-1 text-sm font-medium ${
                  trends[metric.window_key].change_percent > 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {trends[metric.window_key].change_percent > 0 ? '+' : ''}
                  {trends[metric.window_key].change_percent.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading metrics...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Live Metrics</h1>
          <p className="text-gray-600 mt-1">Real-time aggregated metrics and trends</p>
        </div>
        <div className="text-sm text-gray-500">
          Auto-refreshing every 5 seconds
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {currentMetrics.map((metric, index) => (
          <MetricCard key={index} metric={metric} />
        ))}
      </div>

      {/* Detailed View Modal/Panel */}
      {selectedMetric && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-96 overflow-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 capitalize">
                {selectedMetric.metric_name.replace('_', ' ')} Details
              </h2>
              <button 
                onClick={() => setSelectedMetric(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              {Object.entries(selectedMetric.aggregations || {}).map(([key, value]) => (
                <div key={key} className="bg-gray-50 rounded-lg p-3">
                  <p className="text-sm text-gray-600 capitalize">
                    {key.replace('_', ' ')}
                  </p>
                  <p className="text-lg font-semibold text-gray-900">
                    {typeof value === 'number' ? value.toFixed(2) : value}
                  </p>
                </div>
              ))}
            </div>
            
            <div className="text-sm text-gray-600 space-y-1">
              <p><strong>Window Key:</strong> {selectedMetric.window_key}</p>
              <p><strong>Last Updated:</strong> {selectedMetric.timestamp}</p>
              <p><strong>Total Processed:</strong> {selectedMetric.total_processed}</p>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {currentMetrics.length === 0 && !loading && (
        <div className="text-center py-12">
          <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Metrics Available</h3>
          <p className="text-gray-600">
            Metrics will appear here once the aggregation engine starts processing data.
          </p>
        </div>
      )}
    </div>
  );
};

export default Metrics;
