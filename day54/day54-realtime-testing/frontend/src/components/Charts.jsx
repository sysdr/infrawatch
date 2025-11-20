// Lazy-loaded charts component for code splitting
import React, { Suspense } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell
} from 'recharts';

// Loading fallback for charts
const ChartSkeleton = ({ height = 200 }) => (
  <div className="animate-pulse" style={{ height }}>
    <div className="h-full bg-gray-200 rounded"></div>
  </div>
);

export const LatencyChart = React.memo(({ data }) => (
  <ResponsiveContainer width="100%" height={200}>
    <BarChart data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="name" />
      <YAxis />
      <Tooltip />
      <Bar dataKey="value" radius={[4, 4, 0, 0]}>
        {data.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={entry.fill} />
        ))}
      </Bar>
    </BarChart>
  </ResponsiveContainer>
));

export const ThroughputChart = React.memo(({ data }) => (
  <ResponsiveContainer width="100%" height={200}>
    <LineChart data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="time" />
      <YAxis />
      <Tooltip />
      <Line 
        type="monotone" 
        dataKey="throughput" 
        stroke="#8B5CF6" 
        strokeWidth={2}
        dot={false}
      />
    </LineChart>
  </ResponsiveContainer>
));

export const ConnectionChart = React.memo(({ data }) => (
  <ResponsiveContainer width="100%" height={100}>
    <LineChart data={data}>
      <Line 
        type="monotone" 
        dataKey="connections" 
        stroke="#10B981" 
        strokeWidth={2}
        dot={false}
      />
    </LineChart>
  </ResponsiveContainer>
));

// Wrapper with Suspense for lazy loading
export const ChartWrapper = ({ children, height = 200 }) => (
  <Suspense fallback={<ChartSkeleton height={height} />}>
    {children}
  </Suspense>
);

