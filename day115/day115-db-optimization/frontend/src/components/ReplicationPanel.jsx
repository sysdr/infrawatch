import React from 'react';
import { Table, Tag, Button, Progress, Tooltip } from 'antd';
import { ThunderboltOutlined } from '@ant-design/icons';

export default function ReplicationPanel({ replication, connections, bloat, onVacuum }) {
  const lagMs = replication?.current_router_lag_ms || 0;
  const lagColor = lagMs < 10 ? '#52b788' : lagMs < 100 ? '#fca311' : '#e63946';
  const connPct = connections?.utilization_pct || 0;

  return (
    <div className="panel-card">
      <div className="panel-title">Replication & Health</div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 14 }}>
        <div style={{
          background: '#f0fdf4', borderRadius: 8, padding: '10px 14px',
          border: '1px solid #d8f3dc'
        }}>
          <div style={{ fontSize: 10, color: '#74c69d', textTransform: 'uppercase', marginBottom: 4 }}>Replica Lag</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: lagColor }}>
            {lagMs < 1 ? '< 1ms' : `${Math.round(lagMs)}ms`}
          </div>
          <div style={{ fontSize: 10, color: '#aaa', marginTop: 2 }}>
            {replication?.has_replica ? 'Streaming replication' : 'Single-node mode'}
          </div>
          {replication?.has_replica && (
            <Tag color={replication.routing_to_replica ? 'green' : 'orange'} style={{ marginTop: 4, fontSize: 10 }}>
              {replication.routing_to_replica ? 'Routing → Replica' : 'Routing → Primary'}
            </Tag>
          )}
        </div>
        <div style={{
          background: '#f0fdf4', borderRadius: 8, padding: '10px 14px',
          border: '1px solid #d8f3dc'
        }}>
          <div style={{ fontSize: 10, color: '#74c69d', textTransform: 'uppercase', marginBottom: 4 }}>Connections</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: '#1b4332' }}>
            {connections?.total_connections || 0}
          </div>
          <Progress
            percent={connPct} size="small"
            strokeColor={connPct > 80 ? '#e63946' : '#52b788'}
            showInfo={false} style={{ marginTop: 4 }}
          />
          <div style={{ fontSize: 10, color: '#aaa' }}>{connPct}% of {connections?.max_connections}</div>
        </div>
      </div>

      <div style={{ marginBottom: 8, fontSize: 12, fontWeight: 600, color: '#1b4332' }}>
        Table Bloat (top tables)
      </div>
      <Table
        dataSource={bloat?.slice(0, 5) || []}
        rowKey="tablename"
        size="small"
        pagination={false}
        columns={[
          {
            title: 'Table', dataIndex: 'tablename',
            render: v => <span style={{ fontSize: 11, color: '#2d6a4f' }}>{v}</span>
          },
          {
            title: 'Bloat', dataIndex: 'bloat_pct', width: 70,
            render: v => (
              <span style={{
                fontWeight: 700, fontSize: 12,
                color: v > 10 ? '#e63946' : v > 5 ? '#fca311' : '#52b788'
              }}>{v}%</span>
            )
          },
          {
            title: 'Dead Rows', dataIndex: 'dead_rows', width: 85,
            render: v => <span style={{ fontSize: 11, color: '#999' }}>{Number(v).toLocaleString()}</span>
          },
          {
            title: '', width: 65,
            render: (_, r) => (
              <Tooltip title="Run VACUUM ANALYZE">
                <Button size="small" icon={<ThunderboltOutlined />}
                  onClick={() => onVacuum(r.tablename)}
                  style={{ fontSize: 10, borderColor: '#74c69d', color: '#2d6a4f' }}>
                  VACUUM
                </Button>
              </Tooltip>
            )
          }
        ]}
        style={{ fontSize: 11 }}
      />
    </div>
  );
}
