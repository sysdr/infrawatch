import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Button, Alert } from 'antd';
import { ReloadOutlined, CheckCircleOutlined, CloseCircleOutlined, PlayCircleOutlined } from '@ant-design/icons';
import axios from 'axios';
import './Dashboard.css';

const API = process.env.REACT_APP_API_URL || '';

export default function Dashboard() {
  const [data, setData] = useState({ jobs: 0, executions: 0, completed: 0, failed: 0, running: 0, utilization: {} });
  const [executions, setExecutions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [demoLoading, setDemoLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/api/dashboard`);
      setData(r.data);
      const e = await axios.get(`${API}/api/executions`);
      setExecutions(e.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const runDemo = async () => {
    setDemoLoading(true);
    try {
      await axios.post(`${API}/api/jobs`, { name: 'demo-ui-' + Date.now(), command: 'echo demo' });
      const jobs = (await axios.get(`${API}/api/jobs`)).data;
      for (const j of (jobs.slice(0, 3))) {
        await axios.post(`${API}/api/jobs/${j.id}/trigger`).catch(() => {});
      }
      await fetchData();
    } catch (e) { console.error(e); }
    setDemoLoading(false);
  };

  useEffect(() => { fetchData(); const iv = setInterval(fetchData, 5000); return () => clearInterval(iv); }, []);

  const hasData = data.executions > 0 || data.jobs > 0;

  return (
    <div className="dashboard">
      <h1>Scheduler Dashboard</h1>
      <p>Day 102: Scheduling & Triggers - Metrics updated by demo</p>
      {!hasData && <Alert message="No data yet. Run demo: ./run_demo.sh or click Run Demo below." type="info" style={{ marginBottom: 16 }} />}
      <Row gutter={[16, 16]}>
        <Col span={6}><Card><Statistic title="Jobs" value={data.jobs} /></Card></Col>
        <Col span={6}><Card><Statistic title="Executions" value={data.executions} /></Card></Col>
        <Col span={6}><Card><Statistic title="Completed" value={data.completed} prefix={<CheckCircleOutlined />} /></Card></Col>
        <Col span={6}><Card><Statistic title="Failed" value={data.failed} prefix={<CloseCircleOutlined />} /></Card></Col>
      </Row>
      {data.utilization && Object.keys(data.utilization).length > 0 && (
        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          {Object.entries(data.utilization).map(([k, v]) => (
            <Col span={8} key={k}><Card title={k}><Statistic title="Utilization" value={v.utilization_pct || 0} suffix="%" /></Card></Col>
          ))}
        </Row>
      )}
      <Card title="Recent Executions" extra={
        <span>
          <Button icon={<PlayCircleOutlined />} onClick={runDemo} loading={demoLoading} style={{ marginRight: 8 }}>Run Demo</Button>
          <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading}>Refresh</Button>
        </span>
      }>
        <Table dataSource={executions} rowKey="id" columns={[
          { title: 'ID', dataIndex: 'id', key: 'id', render: v => (v || '').slice(0, 8) },
          { title: 'Job ID', dataIndex: 'job_id', key: 'job_id', render: v => (v || '').slice(0, 8) },
          { title: 'State', dataIndex: 'state', key: 'state' },
          { title: 'Trigger', dataIndex: 'trigger_type', key: 'trigger_type' }
        ]} pagination={{ pageSize: 10 }} />
      </Card>
    </div>
  );
}
