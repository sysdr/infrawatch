import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

const MetricsChart = ({ data, metricName, loading, cacheHit }) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!data || !data.data_points || data.data_points.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-800">Metrics Chart</h3>
        <div className="text-center py-12 text-gray-500">
          No data available for the selected time range
        </div>
      </div>
    );
  }

  // Format data for recharts
  const chartData = data.data_points.map(point => ({
    timestamp: new Date(point.timestamp).getTime(),
    value: point.value,
    formattedTime: format(new Date(point.timestamp), 'MMM dd, HH:mm')
  }));

  // Calculate stats
  const values = chartData.map(d => d.value);
  const avg = values.reduce((a, b) => a + b, 0) / values.length;
  const min = Math.min(...values);
  const max = Math.max(...values);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          {metricName} - {data.interval} intervals
        </h3>
        <div className="flex items-center space-x-4 text-sm">
          <span className={`px-2 py-1 rounded-full text-xs ${cacheHit ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}`}>
            {cacheHit ? 'Cache Hit' : 'Database Query'}
          </span>
          <span className="text-gray-600">
            {data.total_points} points
          </span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6 text-center">
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-sm text-gray-600">Average</div>
          <div className="text-lg font-semibold text-blue-600">
            {avg.toFixed(2)}
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-sm text-gray-600">Minimum</div>
          <div className="text-lg font-semibold text-green-600">
            {min.toFixed(2)}
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-sm text-gray-600">Maximum</div>
          <div className="text-lg font-semibold text-red-600">
            {max.toFixed(2)}
          </div>
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="timestamp"
              type="number"
              scale="time"
              domain={['dataMin', 'dataMax']}
              tickFormatter={(timestamp) => format(new Date(timestamp), 'HH:mm')}
            />
            <YAxis />
            <Tooltip 
              labelFormatter={(timestamp) => format(new Date(timestamp), 'MMM dd, yyyy HH:mm')}
              formatter={(value) => [value.toFixed(2), metricName]}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="#2563eb" 
              strokeWidth={2}
              dot={false}
              name={metricName}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default MetricsChart;
