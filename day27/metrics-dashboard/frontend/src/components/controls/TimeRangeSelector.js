import React from 'react';
import { Clock } from 'lucide-react';

const TimeRangeSelector = ({ selectedRange, onRangeChange }) => {
  const ranges = [
    { value: '1h', label: 'Last Hour' },
    { value: '24h', label: 'Last 24 Hours' },
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' }
  ];

  return (
    <div className="wp-card">
      <div className="flex items-center gap-2 mb-3">
        <Clock size={16} className="text-wp-gray" />
        <span className="font-medium">Time Range</span>
      </div>
      
      <div className="flex flex-wrap gap-2">
        {ranges.map(range => (
          <button
            key={range.value}
            onClick={() => onRangeChange(range.value)}
            className={`px-3 py-1 rounded text-sm transition-colors ${
              selectedRange === range.value
                ? 'bg-wp-blue text-white'
                : 'bg-wp-gray-light text-wp-gray hover:bg-gray-200'
            }`}
          >
            {range.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default TimeRangeSelector;
