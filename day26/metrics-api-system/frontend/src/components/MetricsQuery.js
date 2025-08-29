import React, { useState, useEffect } from 'react';
import DatePicker from 'react-datepicker';
import { format, subDays } from 'date-fns';
import 'react-datepicker/dist/react-datepicker.css';

const MetricsQuery = ({ onQuerySubmit, loading }) => {
  const [formData, setFormData] = useState({
    metricName: 'cpu_usage_percent',
    startTime: subDays(new Date(), 1),
    endTime: new Date(),
    interval: '5m',
    aggregation: 'avg'
  });

  const [availableMetrics, setAvailableMetrics] = useState([]);

  useEffect(() => {
    fetchAvailableMetrics();
  }, []);

  const fetchAvailableMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/metrics/list');
      const data = await response.json();
      setAvailableMetrics(data.metrics || []);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onQuerySubmit({
      ...formData,
      startTime: formData.startTime.toISOString(),
      endTime: formData.endTime.toISOString()
    });
  };

  const handleExport = async (exportFormat) => {
    const params = new URLSearchParams({
      metric_name: formData.metricName,
      start_time: formData.startTime.toISOString(),
      end_time: formData.endTime.toISOString(),
      interval: formData.interval,
      aggregation: formData.aggregation,
      format: exportFormat
    });

    try {
      const response = await fetch(`http://localhost:8000/api/v1/metrics/export?${params}`);
      
      if (exportFormat === 'csv') {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${formData.metricName}_${format(formData.startTime, 'yyyyMMdd')}.csv`;
        a.click();
      } else {
        const data = await response.json();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${formData.metricName}_${format(formData.startTime, 'yyyyMMdd')}.json`;
        a.click();
      }
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">Query Metrics</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Metric Name
            </label>
            <select
              value={formData.metricName}
              onChange={(e) => setFormData({...formData, metricName: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {availableMetrics.map(metric => (
                <option key={metric} value={metric}>{metric}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Start Time
            </label>
            <DatePicker
              selected={formData.startTime}
              onChange={(date) => setFormData({...formData, startTime: date})}
              showTimeSelect
              dateFormat="MMM d, yyyy HH:mm"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End Time
            </label>
            <DatePicker
              selected={formData.endTime}
              onChange={(date) => setFormData({...formData, endTime: date})}
              showTimeSelect
              dateFormat="MMM d, yyyy HH:mm"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Interval
            </label>
            <select
              value={formData.interval}
              onChange={(e) => setFormData({...formData, interval: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="1m">1 minute</option>
              <option value="5m">5 minutes</option>
              <option value="15m">15 minutes</option>
              <option value="1h">1 hour</option>
              <option value="1d">1 day</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Aggregation
            </label>
            <select
              value={formData.aggregation}
              onChange={(e) => setFormData({...formData, aggregation: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="avg">Average</option>
              <option value="sum">Sum</option>
              <option value="min">Minimum</option>
              <option value="max">Maximum</option>
              <option value="p50">50th Percentile</option>
              <option value="p95">95th Percentile</option>
              <option value="p99">99th Percentile</option>
            </select>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 pt-4">
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Querying...' : 'Query Metrics'}
          </button>
          
          <button
            type="button"
            onClick={() => handleExport('json')}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            Export JSON
          </button>
          
          <button
            type="button"
            onClick={() => handleExport('csv')}
            className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700"
          >
            Export CSV
          </button>
        </div>
      </form>
    </div>
  );
};

export default MetricsQuery;
