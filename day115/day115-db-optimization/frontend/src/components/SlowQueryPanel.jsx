import React, { useState } from 'react';
import { Table, Tag, Modal, Typography, Button, Tooltip, Badge } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import axios from 'axios';
const { Text } = Typography;
const API = process.env.REACT_APP_API_URL || '';

const severityColor = { critical: '#e63946', warning: '#fca311', ok: '#52b788' };

export default function SlowQueryPanel({ queries }) {
  const [explainModal, setExplainModal] = useState(null);
  const [loadingExplain, setLoadingExplain] = useState(false);

  const showExplain = async (queryId) => {
    setLoadingExplain(true);
    try {
      const r = await axios.get(`${API}/api/queries/explain/${queryId}`);
      setExplainModal(r.data);
    } catch (e) {
      setExplainModal({ plan: 'Error fetching plan: ' + e.message, query: '' });
    } finally {
      setLoadingExplain(false);
    }
  };

  const columns = [
    {
      title: 'Query', dataIndex: 'query', ellipsis: true,
      render: (v) => <Tooltip title={v}><Text code style={{ fontSize: 11 }}>{v?.substring(0, 55)}...</Text></Tooltip>
    },
    {
      title: 'Avg Latency', dataIndex: 'avg_ms', width: 110, sorter: (a, b) => b.avg_ms - a.avg_ms,
      defaultSortOrder: 'ascend',
      render: (v, r) => (
        <span className={`latency-badge latency-${r.severity}`}>{v}ms</span>
      )
    },
    {
      title: 'Calls', dataIndex: 'calls', width: 80,
      render: v => <span style={{ color: '#2d6a4f', fontWeight: 600 }}>{Number(v).toLocaleString()}</span>
    },
    {
      title: 'Total ms', dataIndex: 'total_ms', width: 90,
      render: v => <span style={{ fontSize: 12, color: '#666' }}>{Number(v).toFixed(0)}</span>
    },
    {
      title: 'Cache Hit', width: 85,
      render: (_, r) => {
        const total = (r.shared_blks_hit || 0) + (r.shared_blks_read || 0);
        const pct = total > 0 ? Math.round((r.shared_blks_hit / total) * 100) : 100;
        return <span style={{ color: pct >= 95 ? '#52b788' : '#e63946', fontWeight: 600 }}>{pct}%</span>;
      }
    },
    {
      title: '', width: 70,
      render: (_, r) => (
        <Button size="small" icon={<SearchOutlined />}
          onClick={() => showExplain(r.queryid)}
          style={{ borderColor: '#52b788', color: '#2d6a4f', fontSize: 11 }}
        >PLAN</Button>
      )
    }
  ];

  return (
    <div className="panel-card">
      <div className="panel-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>Slow Query Analysis</span>
        <Badge count={queries.filter(q => q.severity === 'critical').length}
          style={{ backgroundColor: '#e63946' }}
          overflowCount={99}
        />
      </div>
      <Table
        dataSource={queries}
        columns={columns}
        rowKey="queryid"
        size="small"
        pagination={{ pageSize: 8, size: 'small' }}
        rowClassName={(r) => r.severity === 'critical' ? 'critical-row' : ''}
        scroll={{ x: true }}
        style={{ fontSize: 12 }}
      />
      <Modal
        title="EXPLAIN ANALYZE Plan"
        open={!!explainModal}
        onCancel={() => setExplainModal(null)}
        footer={null}
        width={720}
      >
        {explainModal && (
          <>
            <Text type="secondary" style={{ fontSize: 11, display: 'block', marginBottom: 8 }}>
              {explainModal.query?.substring(0, 100)}
            </Text>
            <pre style={{
              background: '#f0f9f4', padding: 12, borderRadius: 6,
              fontSize: 11, overflow: 'auto', maxHeight: 400,
              border: '1px solid #b7e4c7', color: '#1b4332'
            }}>{explainModal.plan}</pre>
          </>
        )}
      </Modal>
    </div>
  );
}
