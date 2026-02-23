import React from 'react';
import { Row, Col, Typography, Alert, Spin, Button } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { useSummary } from '../hooks/useMetrics';
import VitalCard from '../components/performance/VitalCard';
import SummaryStats from '../components/dashboard/SummaryStats';
import VitalsChart from '../components/dashboard/VitalsChart';
import BundleTable from '../components/dashboard/BundleTable';

const { Title, Text } = Typography;
const VITALS = ['LCP', 'CLS', 'FID', 'TTFB', 'INP'];

export default function Dashboard() {
  const { data, error, loading, refresh } = useSummary(24, 15000);

  if (loading) return (
    <div style={{ display: 'flex', justifyContent: 'center', padding: 80 }}>
      <Spin size="large" tip="Loading performance data..." />
    </div>
  );

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <Title level={2} style={{ margin: 0, color: '#1b4332' }}>Performance Overview</Title>
          <Text type="secondary">Real-user metrics — auto-refreshes every 15s</Text>
        </div>
        <Button icon={<ReloadOutlined />} onClick={refresh} type="primary" ghost>Refresh</Button>
      </div>

      {error && <Alert type="error" message={`API Error: ${error}`} style={{ marginBottom: 16 }} />}

      <SummaryStats summary={data} />

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        {VITALS.map(v => (
          <Col key={v} xs={24} sm={12} md={8} lg={6} xl={4}>
            <VitalCard metric={v} stats={data?.vitals?.[v]} />
          </Col>
        ))}
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <VitalsChart metric="LCP" />
        </Col>
        <Col xs={24} lg={12}>
          <VitalsChart metric="CLS" />
        </Col>
      </Row>

      <div style={{ marginTop: 16 }}>
        <BundleTable bundles={data?.bundles} />
      </div>
    </div>
  );
}
