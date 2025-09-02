import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format, parseISO } from 'date-fns';

const MetricLineChart = ({ data, metricName, color = '#0073aa' }) => {
  const chartData = useMemo(() => {
    return data.map(point => ({
      ...point,
      timestamp: new Date(point.timestamp).getTime(),
      formattedTime: format(parseISO(point.timestamp), 'HH:mm:ss')
    }));
  }, [data]);

  const formatTooltip = (value, name, props) => {
    return [
      `${value.toFixed(2)}`,
      metricName
    ];
  };

  const formatLabel = (timestamp) => {
    return format(new Date(timestamp), 'HH:mm:ss dd/MM');
  };

  return (
    <div className="wp-card h-80">
      <h3 className="text-lg font-semibold mb-4 capitalize">
        {metricName?.replace('_', ' ')} Metrics
      </h3>
      
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="timestamp"
            type="number"
            scale="time"
            domain={['dataMin', 'dataMax']}
            tickFormatter={formatLabel}
            stroke="#666"
          />
          <YAxis stroke="#666" />
          <Tooltip 
            formatter={formatTooltip}
            labelFormatter={formatLabel}
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #ccc',
              borderRadius: '4px'
            }}
          />
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke={color} 
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: color }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default MetricLineChart;
