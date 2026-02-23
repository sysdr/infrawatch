import React from 'react';
import { Typography, Card, Row, Col, Statistic, Table, Tag, Progress } from 'antd';
import { CloudServerOutlined } from '@ant-design/icons';
import { useSummary } from '../hooks/useMetrics';

const { Title, Text, Paragraph } = Typography;

const strategies = [
  { strategy: 'Cache-First', applies: 'JS/CSS with content hash', benefit: 'Instant on repeat visits', when: 'Assets never change after deploy' },
  { strategy: 'Network-First', applies: '/api/** endpoints', benefit: 'Always fresh data, offline fallback', when: 'Dynamic data' },
  { strategy: 'Stale-While-Revalidate', applies: 'Fonts, avatars, images', benefit: 'Instant serve + background refresh', when: 'Can tolerate 1 stale request' },
];

export default function SWPage() {
  const { data } = useSummary();
  const sw = data?.serviceWorker || {};

  return (
    <div>
      <Title level={2} style={{ color: '#1b4332', marginBottom: 4 }}>Service Worker</Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
        Workbox cache strategies and hit ratio
      </Text>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={8}>
          <Card style={{ borderRadius: 12, borderTop: '3px solid #52b788' }}>
            <Statistic title="Cache Hit Ratio" value={sw.hit_ratio_pct || 0} suffix="%" valueStyle={{ color: '#2d6a4f', fontWeight: 700 }} />
            <Progress percent={sw.hit_ratio_pct || 0} strokeColor="#52b788" showInfo={false} style={{ marginTop: 8 }} />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card style={{ borderRadius: 12 }}>
            <Statistic title="Cache Hits" value={sw.cache_hits || 0} prefix={<CloudServerOutlined />} valueStyle={{ color: '#52c41a' }} />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card style={{ borderRadius: 12 }}>
            <Statistic title="Total Requests" value={sw.total_requests || 0} valueStyle={{ color: '#1890ff' }} />
          </Card>
        </Col>
      </Row>

      <Card title="Cache Strategy Reference" style={{ marginTop: 16, borderRadius: 12 }}>
        <Table
          dataSource={strategies.map((s, i) => ({ ...s, key: i }))}
          pagination={false}
          size="small"
          columns={[
            { title: 'Strategy', dataIndex: 'strategy', render: v => <Tag color="green">{v}</Tag> },
            { title: 'Applies To', dataIndex: 'applies' },
            { title: 'Benefit', dataIndex: 'benefit' },
            { title: 'Use When', dataIndex: 'when' },
          ]}
        />
      </Card>
    </div>
  );
}
