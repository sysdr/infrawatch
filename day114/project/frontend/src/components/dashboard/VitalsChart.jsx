import React from 'react';
import { Card, Typography, Spin } from 'antd';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts';
import { useTimeseries } from '../../hooks/useMetrics';
import { format } from 'date-fns';

const { Title } = Typography;
const THRESHOLDS = { LCP: 2500, FID: 100, CLS: 0.1, TTFB: 800, INP: 200 };

export default function VitalsChart({ metric = 'LCP' }) {
  const { data, loading } = useTimeseries(metric, 6);
  const threshold = THRESHOLDS[metric];

  const chartData = data.map(d => ({
    value: d.value,
    time: format(new Date(d.time), 'HH:mm'),
  }));

  return (
    <Card
      title={<Title level={5} style={{ margin: 0, color: '#1b4332' }}>{metric} — Last 6 Hours</Title>}
      style={{ borderRadius: 12 }}
    >
      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}>
          <Spin size="large" />
        </div>
      ) : chartData.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
          No data yet — navigate around the app to generate metrics
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="time" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            {threshold && (
              <ReferenceLine y={threshold} stroke="#ff4d4f" strokeDasharray="4 4"
                label={{ value: 'Target', fill: '#ff4d4f', fontSize: 10 }} />
            )}
            <Line
              type="monotone" dataKey="value" stroke="#2d6a4f"
              strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </Card>
  );
}
