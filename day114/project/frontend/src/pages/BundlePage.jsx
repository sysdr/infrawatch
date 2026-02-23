import React from 'react';
import { Typography, Row, Col } from 'antd';
import { useSummary } from '../hooks/useMetrics';
import BundleTable from '../components/dashboard/BundleTable';
import SummaryStats from '../components/dashboard/SummaryStats';

const { Title, Text } = Typography;

export default function BundlePage() {
  const { data } = useSummary();
  return (
    <div>
      <Title level={2} style={{ color: '#1b4332', marginBottom: 4 }}>Bundle Analysis</Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
        JavaScript chunk sizes and cache performance
      </Text>
      <SummaryStats summary={data} />
      <div style={{ marginTop: 16 }}>
        <BundleTable bundles={data?.bundles} />
      </div>
    </div>
  );
}
