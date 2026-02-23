import React, { useState } from 'react';
import { Typography, Row, Col, Select } from 'antd';
import { useSummary } from '../hooks/useMetrics';
import VitalCard from '../components/performance/VitalCard';
import VitalsChart from '../components/dashboard/VitalsChart';

const { Title, Text } = Typography;
const VITALS = ['LCP', 'CLS', 'FID', 'TTFB', 'INP'];

export default function VitalsPage() {
  const [hours, setHours] = useState(24);
  const { data } = useSummary(hours);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <Title level={2} style={{ margin: 0, color: '#1b4332' }}>Core Web Vitals</Title>
          <Text type="secondary">Google's user experience metrics</Text>
        </div>
        <Select value={hours} onChange={setHours} options={[
          { value: 1, label: 'Last 1h' }, { value: 6, label: 'Last 6h' },
          { value: 24, label: 'Last 24h' }, { value: 168, label: 'Last 7d' },
        ]} style={{ width: 120 }} />
      </div>

      <Row gutter={[16, 16]}>
        {VITALS.map(v => (
          <Col key={v} xs={24} sm={12} lg={8}>
            <VitalCard metric={v} stats={data?.vitals?.[v]} />
          </Col>
        ))}
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        {VITALS.map(v => (
          <Col key={v} xs={24} lg={12}>
            <VitalsChart metric={v} />
          </Col>
        ))}
      </Row>
    </div>
  );
}
