import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Button, Alert } from 'antd';
import { ReloadOutlined, ApiOutlined, LinkOutlined, CheckCircleOutlined } from '@ant-design/icons';
import axios from 'axios';
import './Dashboard.css';

const API = process.env.REACT_APP_API_URL || '';

export default function Dashboard() {
  const [data, setData] = useState({ integrations: 0, webhooks_received: 0, events_processed: 0 });
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [demoLoading, setDemoLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/api/dashboard`);
      setData(r.data);
      const i = await axios.get(`${API}/api/integrations`);
      setIntegrations(i.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const runDemo = async () => {
    setDemoLoading(true);
    try {
      await axios.post(`${API}/api/integrations`, { name: 'demo-ui-' + Date.now(), type: 'webhook' });
      const list = (await axios.get(`${API}/api/integrations`)).data;
      for (const i of list.slice(0, 3)) {
        await axios.post(`${API}/api/webhook/${i.id}`, { source: 'ui-demo', payload: {} }).catch(() => {});
      }
      await fetchData();
    } catch (e) { console.error(e); }
    setDemoLoading(false);
  };

  useEffect(() => { fetchData(); const iv = setInterval(fetchData, 5000); return () => clearInterval(iv); }, []);

  const hasData = data.webhooks_received > 0 || data.integrations > 0;

  return (
    <div className="dashboard">
      <h1>Integration Framework Dashboard</h1>
      <p>Day 103: Webhooks &amp; integrations - metrics updated by demo</p>
      {!hasData && <Alert message="No data yet. Run demo: ./run_demo.sh or click Run Demo below." type="info" style={{ marginBottom: 16 }} />}
      <Row gutter={[16, 16]}>
        <Col span={8}><Card><Statistic title="Integrations" value={data.integrations} prefix={<LinkOutlined />} /></Card></Col>
        <Col span={8}><Card><Statistic title="Webhooks Received" value={data.webhooks_received} prefix={<ApiOutlined />} /></Card></Col>
        <Col span={8}><Card><Statistic title="Events Processed" value={data.events_processed} prefix={<CheckCircleOutlined />} /></Card></Col>
      </Row>
      <Card title="Integrations" extra={
        <span>
          <Button icon={<ApiOutlined />} onClick={runDemo} loading={demoLoading} style={{ marginRight: 8 }}>Run Demo</Button>
          <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading}>Refresh</Button>
        </span>
      }>
        <Table dataSource={integrations} rowKey="id" columns={[
          { title: 'ID', dataIndex: 'id', key: 'id', render: v => (v || '').slice(0, 8) },
          { title: 'Name', dataIndex: 'name', key: 'name' },
          { title: 'Type', dataIndex: 'type', key: 'type' }
        ]} pagination={{ pageSize: 10 }} />
      </Card>
    </div>
  );
}
