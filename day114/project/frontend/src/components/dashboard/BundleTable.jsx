import React from 'react';
import { Table, Tag, Card, Typography, Progress } from 'antd';

const { Title } = Typography;

const columns = [
  { title: 'Chunk', dataIndex: 'chunk', key: 'chunk',
    render: t => <code style={{ fontSize: 12, background: '#f6ffed', padding: '2px 6px', borderRadius: 4 }}>{t}</code> },
  { title: 'Size (KB)', dataIndex: 'avg_size_kb', key: 'size', sorter: (a, b) => a.avg_size_kb - b.avg_size_kb,
    render: v => (
      <span>
        <span style={{ fontWeight: 600, color: v > 200 ? '#ff4d4f' : '#2d6a4f' }}>{v}</span>
        <Progress percent={Math.min(100, v / 3)} showInfo={false} size="small" strokeColor={v > 200 ? '#ff4d4f' : '#52b788'} style={{ width: 60, display: 'inline-block', marginLeft: 8 }} />
      </span>
    )},
  { title: 'Load (ms)', dataIndex: 'avg_load_ms', key: 'load', sorter: (a, b) => a.avg_load_ms - b.avg_load_ms,
    render: v => <span style={{ color: v > 500 ? '#faad14' : '#52c41a' }}>{v}ms</span> },
  { title: 'Cache Hit', dataIndex: 'cache_ratio', key: 'cache',
    render: v => <Tag color={v >= 80 ? 'green' : v >= 50 ? 'gold' : 'red'}>{v}%</Tag> },
  { title: 'Loads', dataIndex: 'loads', key: 'loads' },
];

export default function BundleTable({ bundles }) {
  return (
    <Card
      title={<Title level={5} style={{ margin: 0, color: '#1b4332' }}>Bundle Chunks</Title>}
      style={{ borderRadius: 12 }}
    >
      <Table
        columns={columns}
        dataSource={(bundles || []).map((b, i) => ({ ...b, key: i }))}
        pagination={false}
        size="small"
        locale={{ emptyText: 'Navigate around the app to generate bundle metrics' }}
      />
    </Card>
  );
}
