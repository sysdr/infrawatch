import React, { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Brush
} from 'recharts';
import { format, parseISO } from 'date-fns';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function MultiSeriesChart({ data }) {
  const [selectedSeries, setSelectedSeries] = useState(
    data.series.map(s => s.name)
  );

  const chartData = data.series[0].data.map((point, idx) => {
    const dataPoint = { timestamp: point.timestamp };
    data.series.forEach(series => {
      dataPoint[series.name] = series.data[idx].value;
    });
    return dataPoint;
  });

  const handleLegendClick = (e) => {
    const { dataKey } = e;
    setSelectedSeries(prev =>
      prev.includes(dataKey)
        ? prev.filter(s => s !== dataKey)
        : [...prev, dataKey]
    );
  };

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="timestamp"
          tickFormatter={(ts) => format(parseISO(ts), 'HH:mm')}
        />
        <YAxis />
        <Tooltip
          labelFormatter={(ts) => format(parseISO(ts), 'MMM dd, HH:mm')}
          formatter={(value) => value.toFixed(2)}
        />
        <Legend onClick={handleLegendClick} />
        <Brush
          dataKey="timestamp"
          height={30}
          stroke="#8884d8"
          tickFormatter={(ts) => format(parseISO(ts), 'HH:mm')}
        />
        {data.series.map((series, idx) => (
          <Line
            key={series.name}
            type="monotone"
            dataKey={series.name}
            stroke={COLORS[idx % COLORS.length]}
            dot={false}
            strokeWidth={2}
            hide={!selectedSeries.includes(series.name)}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
