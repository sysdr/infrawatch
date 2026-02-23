import React from 'react';
import { Row, Col } from 'antd';
import {
  ThunderboltOutlined, ClockCircleOutlined,
  ApiOutlined, SafetyOutlined
} from '@ant-design/icons';

const MetricCard = ({ icon, value, label, color, subtext }) => (
  <div style={{
    background: 'white', borderRadius: 10, padding: '16px 20px',
    boxShadow: '0 1px 4px rgba(0,0,0,0.08)', borderLeft: `4px solid ${color}`,
    display: 'flex', alignItems: 'center', gap: 16
  }}>
    <div style={{
      width: 44, height: 44, borderRadius: 10,
      background: `${color}22`, display: 'flex',
      alignItems: 'center', justifyContent: 'center', fontSize: 20, color
    }}>{icon}</div>
    <div>
      <div style={{ fontSize: 26, fontWeight: 700, color: '#1b4332', lineHeight: 1 }}>{value}</div>
      <div style={{ fontSize: 11, color: '#74c69d', textTransform: 'uppercase', letterSpacing: '0.5px', marginTop: 2 }}>{label}</div>
      {subtext && <div style={{ fontSize: 11, color: '#999', marginTop: 2 }}>{subtext}</div>}
    </div>
  </div>
);

export default function SummaryCards({ summary, connections }) {
  if (!summary) return null;
  const latencyColor = summary.avg_query_latency_ms < 50 ? '#52b788'
    : summary.avg_query_latency_ms < 200 ? '#fca311' : '#e63946';
  return (
    <Row gutter={[12, 12]}>
      <Col xs={12} sm={6}>
        <MetricCard
          icon={<ClockCircleOutlined />}
          value={`${summary.avg_query_latency_ms}ms`}
          label="Avg Latency (p50)"
          color={latencyColor}
          subtext="Top 5 slow queries"
        />
      </Col>
      <Col xs={12} sm={6}>
        <MetricCard
          icon={<ThunderboltOutlined />}
          value={summary.slow_query_count}
          label="Slow Queries"
          color={summary.slow_query_count > 5 ? '#e63946' : '#52b788'}
          subtext="> 100ms threshold"
        />
      </Col>
      <Col xs={12} sm={6}>
        <MetricCard
          icon={<ApiOutlined />}
          value={connections ? `${connections.total_connections}` : '—'}
          label="Active Connections"
          color="#40916c"
          subtext={connections ? `${connections.utilization_pct}% of max` : ''}
        />
      </Col>
      <Col xs={12} sm={6}>
        <MetricCard
          icon={<SafetyOutlined />}
          value={summary.replica_lag_ms < 1 ? '< 1ms' : `${Math.round(summary.replica_lag_ms)}ms`}
          label="Replica Lag"
          color={summary.replica_lag_ms < 100 ? '#52b788' : '#e63946'}
          subtext={summary.routing_to_replica ? 'Routing to replica ✓' : 'Primary only'}
        />
      </Col>
    </Row>
  );
}
