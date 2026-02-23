import React, { useState } from 'react';
import { Table, Button, Tag, Modal, Form, Input, Select, notification, Tooltip } from 'antd';
import { PlusOutlined, WarningOutlined } from '@ant-design/icons';
import axios from 'axios';
const API = process.env.REACT_APP_API_URL || '';

export default function IndexHealthPanel({ indexes, onRefresh }) {
  const [createModal, setCreateModal] = useState(false);
  const [form] = Form.useForm();
  const [creating, setCreating] = useState(false);
  const [notifApi, ctx] = notification.useNotification();

  const handleCreate = async (vals) => {
    setCreating(true);
    try {
      const cols = vals.columns.split(',').map(c => c.trim());
      await axios.post(`${API}/api/indexes/create`, {
        table_name: vals.table_name,
        columns: cols,
        index_type: vals.index_type || 'btree',
      });
      notifApi.success({ message: `Index created on ${vals.table_name}(${vals.columns})` });
      setCreateModal(false);
      form.resetFields();
      onRefresh();
    } catch (e) {
      notifApi.error({ message: 'Index creation failed', description: e.response?.data?.detail || e.message });
    } finally {
      setCreating(false);
    }
  };

  const columns = [
    {
      title: 'Index', dataIndex: 'indexname',
      render: (v, r) => (
        <div>
          <div style={{ fontSize: 12, fontWeight: 600, color: '#1b4332' }}>{v}</div>
          <div style={{ fontSize: 10, color: '#999' }}>{r.tablename}</div>
        </div>
      )
    },
    {
      title: 'Hit Rate', width: 100,
      render: (_, r) => {
        const pct = r.hit_rate_pct || 0;
        const color = pct >= 90 ? '#52b788' : pct >= 50 ? '#fca311' : '#e63946';
        return (
          <div>
            <div style={{ color, fontWeight: 700, fontSize: 13 }}>{pct}%</div>
            <div className="index-bar">
              <div className="index-bar-fill" style={{ width: `${pct}%`, background: color }} />
            </div>
          </div>
        );
      }
    },
    {
      title: 'Scans', dataIndex: 'scans', width: 70,
      render: v => <span style={{ color: '#2d6a4f', fontSize: 12 }}>{Number(v).toLocaleString()}</span>
    },
    {
      title: 'Size', dataIndex: 'index_size', width: 70,
      render: v => <span style={{ fontSize: 12, color: '#666' }}>{v}</span>
    },
    {
      title: 'Status', width: 80,
      render: (_, r) => r.unused
        ? <Tag color="red" style={{ fontSize: 10 }}>UNUSED</Tag>
        : <Tag color="green" style={{ fontSize: 10 }}>ACTIVE</Tag>
    }
  ];

  return (
    <div className="panel-card">
      {ctx}
      <div className="panel-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>Index Health</span>
        <Button size="small" icon={<PlusOutlined />} onClick={() => setCreateModal(true)}
          style={{ background: '#52b788', borderColor: '#40916c', color: 'white', fontSize: 11 }}>
          New Index
        </Button>
      </div>
      <Table
        dataSource={indexes}
        columns={columns}
        rowKey="indexname"
        size="small"
        pagination={{ pageSize: 6, size: 'small' }}
        style={{ fontSize: 12 }}
      />
      <Modal
        title="Create Index CONCURRENTLY"
        open={createModal}
        onCancel={() => setCreateModal(false)}
        onOk={() => form.submit()}
        okText="Create"
        okButtonProps={{ loading: creating, style: { background: '#40916c' } }}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item name="table_name" label="Table" rules={[{ required: true }]}>
            <Select options={[
              { value: 'audit_events', label: 'audit_events' },
              { value: 'users', label: 'users' },
              { value: 'teams', label: 'teams' },
            ]} />
          </Form.Item>
          <Form.Item name="columns" label="Columns (comma-separated)" rules={[{ required: true }]}>
            <Input placeholder="e.g., user_id, created_at" />
          </Form.Item>
          <Form.Item name="index_type" label="Index Type" initialValue="btree">
            <Select options={[
              { value: 'btree', label: 'BTREE (default)' },
              { value: 'gin', label: 'GIN (JSONB/arrays)' },
              { value: 'hash', label: 'HASH (equality only)' },
            ]} />
          </Form.Item>
          <p style={{ fontSize: 12, color: '#74c69d', marginTop: 8 }}>
            Uses CONCURRENTLY — safe on live tables, no write lock.
          </p>
        </Form>
      </Modal>
    </div>
  );
}
