import React, { useState } from 'react';
import { Search, TrendingUp } from 'lucide-react';
import { useMetricNames } from '../../hooks/useMetrics';

const MetricSelector = ({ selectedMetrics, onMetricToggle }) => {
  const { names, loading, error } = useMetricNames();
  const [searchTerm, setSearchTerm] = useState('');

  const filteredNames = names.filter(name =>
    name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) return <div className="wp-card">Loading metrics...</div>;
  if (error) return <div className="wp-card text-red-600">Error: {error}</div>;

  return (
    <div className="wp-card">
      <div className="flex items-center gap-2 mb-3">
        <TrendingUp size={16} className="text-wp-gray" />
        <span className="font-medium">Select Metrics</span>
      </div>

      <div className="relative mb-3">
        <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-wp-gray" />
        <input
          type="text"
          placeholder="Search metrics..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-wp-blue focus:border-transparent"
        />
      </div>

      <div className="max-h-48 overflow-y-auto space-y-1">
        {filteredNames.map(name => (
          <label key={name} className="flex items-center gap-2 p-2 hover:bg-wp-gray-light rounded cursor-pointer">
            <input
              type="checkbox"
              checked={selectedMetrics.includes(name)}
              onChange={() => onMetricToggle(name)}
              className="rounded border-gray-300 text-wp-blue focus:ring-wp-blue"
            />
            <span className="text-sm capitalize">{name.replace('_', ' ')}</span>
          </label>
        ))}
      </div>
    </div>
  );
};

export default MetricSelector;
