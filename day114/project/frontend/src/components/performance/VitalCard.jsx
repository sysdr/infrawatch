import React from 'react';
import { Card, Statistic, Tag, Tooltip } from 'antd';
import { ThunderboltOutlined } from '@ant-design/icons';

const RATING_COLORS = { good: '#52c41a', 'needs-improvement': '#faad14', poor: '#ff4d4f', unknown: '#8c8c8c' };
const DESCRIPTIONS = {
  LCP:  { label: 'Largest Contentful Paint', unit: 'ms', tip: 'Time until the largest element is visible. Target < 2500ms' },
  CLS:  { label: 'Cumulative Layout Shift',  unit: '',   tip: 'Visual stability score. Target < 0.1' },
  FID:  { label: 'First Input Delay',        unit: 'ms', tip: 'Response time to first interaction. Target < 100ms' },
  TTFB: { label: 'Time to First Byte',       unit: 'ms', tip: 'Backend response time. Target < 800ms' },
  INP:  { label: 'Interaction to Next Paint', unit: 'ms', tip: 'Overall interaction responsiveness. Target < 200ms' },
};

export default function VitalCard({ metric, stats }) {
  if (!stats) return null;
  const meta  = DESCRIPTIONS[metric] || { label: metric, unit: 'ms', tip: '' };
  const color = RATING_COLORS[stats.rating] || '#8c8c8c';
  const value = metric === 'CLS' ? stats.avg.toFixed(3) : Math.round(stats.avg);

  return (
    <Tooltip title={meta.tip}>
      <Card
        size="small"
        style={{ borderTop: `3px solid ${color}`, borderRadius: 10 }}
        bodyStyle={{ padding: '16px' }}
      >
        <Statistic
          title={<span style={{ fontSize: 11, color: '#666' }}>{meta.label}</span>}
          value={value}
          suffix={meta.unit}
          prefix={<ThunderboltOutlined style={{ color }} />}
          valueStyle={{ color, fontSize: 24, fontWeight: 700 }}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
          <Tag color={color === '#52c41a' ? 'green' : color === '#faad14' ? 'gold' : 'red'}>
            {stats.rating}
          </Tag>
          <span style={{ fontSize: 11, color: '#999' }}>{stats.count} samples</span>
        </div>
      </Card>
    </Tooltip>
  );
}
