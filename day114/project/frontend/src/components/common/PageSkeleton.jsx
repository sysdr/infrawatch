import React from 'react';
import { Skeleton, Row, Col, Card } from 'antd';

export default function PageSkeleton() {
  return (
    <div>
      <Skeleton.Input active size="large" style={{ width: 300, marginBottom: 24 }} />
      <Row gutter={[16, 16]}>
        {[1, 2, 3, 4].map(i => (
          <Col key={i} xs={24} sm={12} lg={6}>
            <Card><Skeleton active paragraph={{ rows: 2 }} /></Card>
          </Col>
        ))}
      </Row>
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card><Skeleton active paragraph={{ rows: 6 }} /></Card>
        </Col>
      </Row>
    </div>
  );
}
