import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip as RcTooltip, ResponsiveContainer, Cell } from 'recharts';
import { Button, Tag, notification } from 'antd';
import axios from 'axios';
const API = process.env.REACT_APP_API_URL || '';

const COLORS = [
  '#1b4332','#2d6a4f','#40916c','#52b788',
  '#74c69d','#95d5b2','#b7e4c7','#d8f3dc',
  '#40916c','#52b788','#74c69d','#95d5b2'
];

export default function PartitionPanel({ partitions }) {
  const [pruningResult, setPruningResult] = useState(null);
  const [testing, setTesting] = useState(false);
  const [notifApi, ctx] = notification.useNotification();

  const auditParts = partitions.filter(p => p.parent_table === 'audit_events');
  const chartData = auditParts.map((p, i) => ({
    name: p.partition_name.replace('audit_events_', '').replace('_', '-'),
    rows: p.row_count,
    size: p.partition_size,
    idx: i
  }));

  const testPruning = async () => {
    setTesting(true);
    try {
      const r = await axios.get(`${API}/api/partitions/pruning-test?start=2025-05-01&end=2025-06-01`);
      setPruningResult(r.data);
    } catch (e) {
      notifApi.error({ message: 'Pruning test failed' });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="panel-card">
      {ctx}
      <div className="panel-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>Partition Stats — audit_events (2025)</span>
        <Button size="small" onClick={testPruning} loading={testing}
          style={{ background: '#40916c', borderColor: '#2d6a4f', color: 'white', fontSize: 11 }}>
          Test Pruning
        </Button>
      </div>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={chartData} margin={{ top: 4, right: 4, left: -20, bottom: 4 }}>
          <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#2d6a4f' }} />
          <YAxis tick={{ fontSize: 10 }} tickFormatter={v => v > 1000 ? `${(v/1000).toFixed(0)}k` : v} />
          <RcTooltip formatter={(v, n, p) => [`${Number(v).toLocaleString()} rows`, p.payload.size]} />
          <Bar dataKey="rows" radius={[3, 3, 0, 0]}>
            {chartData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 8 }}>
        <span style={{ fontSize: 11, color: '#666' }}>
          {auditParts.length} partitions · {auditParts.reduce((s, p) => s + p.row_count, 0).toLocaleString()} total rows
        </span>
      </div>
      {pruningResult && (
        <div style={{
          marginTop: 10, padding: '10px 14px', background: '#f0fdf4',
          borderRadius: 8, border: '1px solid #b7e4c7'
        }}>
          <div style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={{ fontSize: 12, color: '#2d6a4f', fontWeight: 700 }}>
              Pruning Result: May 2025 query
            </span>
            <Tag color="green">Scanned: {pruningResult.partitions_scanned}/{pruningResult.total_partitions}</Tag>
            <Tag color="success">
              {pruningResult.pruning_efficiency_pct}% eliminated
            </Tag>
          </div>
          <pre style={{
            fontSize: 10, background: '#e8f5e9', padding: 8,
            borderRadius: 4, marginTop: 6, maxHeight: 100, overflow: 'auto',
            color: '#1b4332', border: '1px solid #c8e6c9'
          }}>{pruningResult.plan}</pre>
        </div>
      )}
    </div>
  );
}
