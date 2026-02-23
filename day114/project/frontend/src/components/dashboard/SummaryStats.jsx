import React from 'react';
import { Row, Col, Card, Statistic, Progress, Typography } from 'antd';
import { CloudServerOutlined, RocketOutlined, AppstoreOutlined } from '@ant-design/icons';

const { Text } = Typography;

export default function SummaryStats({ summary }) {
  const sw = summary?.serviceWorker || {};
  const bundles = summary?.bundles || [];
  const totalBundleKB = bundles.reduce((s, b) => s + (b.avg_size_kb || 0), 0);
  const cacheRatio = sw.hit_ratio_pct || 0;

  return (
    <Row gutter={[16, 16]}>
      <Col xs={24} sm={8}>
        <Card style={{ borderRadius: 12 }}>
          <Statistic
            title="SW Cache Hit Ratio"
            value={cacheRatio}
            suffix="%"
            prefix={<CloudServerOutlined style={{ color: '#2d6a4f' }} />}
            valueStyle={{ color: cacheRatio >= 80 ? '#52c41a' : cacheRatio >= 50 ? '#faad14' : '#ff4d4f' }}
          />
          <Progress percent={cacheRatio} strokeColor="#52b788" showInfo={false} style={{ marginTop: 8 }} />
          <Text type="secondary" style={{ fontSize: 11 }}>{sw.cache_hits || 0} / {sw.total_requests || 0} requests</Text>
        </Card>
      </Col>
      <Col xs={24} sm={8}>
        <Card style={{ borderRadius: 12 }}>
          <Statistic
            title="Total Bundle Size"
            value={Math.round(totalBundleKB)}
            suffix="KB"
            prefix={<AppstoreOutlined style={{ color: '#1890ff' }} />}
            valueStyle={{ color: totalBundleKB <= 200 ? '#52c41a' : '#faad14' }}
          />
          <Progress
            percent={Math.min(100, Math.round(totalBundleKB / 500 * 100))}
            strokeColor={totalBundleKB <= 200 ? '#52b788' : '#faad14'}
            showInfo={false} style={{ marginTop: 8 }}
          />
          <Text type="secondary" style={{ fontSize: 11 }}>Target: &lt; 200KB initial</Text>
        </Card>
      </Col>
      <Col xs={24} sm={8}>
        <Card style={{ borderRadius: 12 }}>
          <Statistic
            title="Active Chunks"
            value={bundles.length}
            suffix="chunks"
            prefix={<RocketOutlined style={{ color: '#722ed1' }} />}
            valueStyle={{ color: '#722ed1' }}
          />
          <Text type="secondary" style={{ fontSize: 11 }}>
            {bundles.filter(b => b.cache_ratio >= 80).length} chunks with high cache ratio
          </Text>
        </Card>
      </Col>
    </Row>
  );
}
