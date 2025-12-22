import React, { useMemo } from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { format } from 'date-fns';

export default function MetricChart({ name, data }) {
  const chartData = useMemo(() => {
    return data.map((metric, index) => ({
      index,
      value: metric.value,
      timestamp: new Date(metric.timestamp),
      priority: metric.priority
    }));
  }, [data]);

  const latestValue = data[data.length - 1]?.value || 0;
  const isCritical = data[data.length - 1]?.priority === 'critical';

  const formatName = (name) => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <Card elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" component="div">
            {formatName(name)}
          </Typography>
          <Typography
            variant="h4"
            component="div"
            sx={{
              color: isCritical ? 'error.main' : 'primary.main',
              fontWeight: 'bold'
            }}
          >
            {latestValue.toFixed(1)}
          </Typography>
        </Box>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="index"
              tick={{ fontSize: 12 }}
              stroke="#999"
            />
            <YAxis
              tick={{ fontSize: 12 }}
              stroke="#999"
            />
            <Tooltip
              labelFormatter={(value) => `Point ${value}`}
              formatter={(value) => [value.toFixed(2), name]}
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                border: '1px solid #ccc',
                borderRadius: 4
              }}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke={isCritical ? '#f44336' : '#1976d2'}
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
