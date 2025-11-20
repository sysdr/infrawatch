import React from 'react';

// Memoized component to prevent unnecessary re-renders
export const MetricCard = React.memo(({ title, value, color }) => {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-700 border-blue-200',
    green: 'bg-green-50 text-green-700 border-green-200',
    purple: 'bg-purple-50 text-purple-700 border-purple-200',
    red: 'bg-red-50 text-red-700 border-red-200',
    gray: 'bg-gray-50 text-gray-700 border-gray-200'
  };

  return (
    <div className={`rounded-xl border p-4 ${colorClasses[color]}`}>
      <p className="text-sm font-medium opacity-75">{title}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  );
});

MetricCard.displayName = 'MetricCard';

