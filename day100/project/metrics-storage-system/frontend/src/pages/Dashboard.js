import React, { useState, useEffect, useCallback } from 'react';
import { Card, Row, Col, Statistic, Table, Button, Space, Alert } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ReloadOutlined, DatabaseOutlined, BarChartOutlined, WifiOutlined } from '@ant-design/icons';
import axios from 'axios';
import webSocketService from '../services/websocket';
import './Dashboard.css';

const API = process.env.REACT_APP_API_URL || '';

const Dashboard = () => {
  const [metrics, setMetrics] = useState([]);
  const [summary, setSummary] = useState({ total: 0, cpu_avg: 0, memory_avg: 0, disk_avg: 0 });
  const [loading, setLoading] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [wsError, setWsError] = useState(null);

  const fetchMetrics = useCallback(async () => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/api/metrics`);
      const data = r.data;
      setMetrics(data.metrics || []);
      setSummary(data.summary || { total: 0, cpu_avg: 0, memory_avg: 0, disk_avg: 0 });
    } catch (e) {
      console.error('Fetch metrics failed:', e);
      setMetrics([]);
      setSummary({ total: 0, cpu_avg: 0, memory_avg: 0, disk_avg: 0 });
    } finally {
      setLoading(false);
    }
  }, []);

  const handleWebSocketMessage = useCallback((data) => {
    if (data.type === 'metrics_update' && data.data) {
      const newMetric = {
        timestamp: new Date().toLocaleTimeString(),
        cpu: data.data.cpu_usage,
        memory: data.data.memory_usage,
        disk: data.data.disk_usage,
        network: data.data.network_io
      };
      setMetrics(prev => [...prev.slice(-19), newMetric]);
      if (data.data.cpu_usage) setSummary(s => ({ ...s, cpu_avg: data.data.cpu_usage, memory_avg: data.data.memory_usage, disk_avg: data.data.disk_usage }));
    }
  }, []);

  useEffect(() => {
    fetchMetrics();
    webSocketService.addMessageHandler(handleWebSocketMessage);
    webSocketService.connect();
    const iv = setInterval(() => {
      setWsConnected(webSocketService.isConnected);
      setWsError(webSocketService.isConnected ? null : 'WebSocket disconnected');
    }, 1000);
    return () => {
      webSocketService.removeMessageHandler(handleWebSocketMessage);
      webSocketService.disconnect();
      clearInterval(iv);
    };
  }, [fetchMetrics, handleWebSocketMessage]);

  const chartData = metrics.length > 0 ? metrics : [];
  const cpuAvg = summary.cpu_avg || (chartData.length ? (chartData.reduce((s, m) => s + (m.cpu || 0), 0) / chartData.length).toFixed(1) : 0);
  const memAvg = summary.memory_avg || (chartData.length ? (chartData.reduce((s, m) => s + (m.memory || 0), 0) / chartData.length).toFixed(1) : 0);
  const totalCount = summary.total || chartData.length;

  const columns = [
    { title: 'Timestamp', dataIndex: 'timestamp', key: 'timestamp' },
    { title: 'CPU (%)', dataIndex: 'cpu', key: 'cpu', render: v => v != null ? v : '-' },
    { title: 'Memory (%)', dataIndex: 'memory', key: 'memory', render: v => v != null ? v : '-' },
    { title: 'Disk (%)', dataIndex: 'disk', key: 'disk', render: v => v != null ? v : '-' },
  ];

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1><DatabaseOutlined /> Metrics Storage Dashboard</h1>
        <p>Day 100: Real-time metrics - start.sh runs demo automatically for non-zero data</p>
      </div>
      {wsError && <Alert message="WebSocket Issue" description={wsError} type="warning" showIcon style={{ marginBottom: 16 }} />}
      {wsConnected && <Alert message="Real-time Updates Active" type="success" icon={<WifiOutlined />} style={{ marginBottom: 16 }} />}
      <Row gutter={[16, 16]} className="stats-row">
        <Col span={6}><Card><Statistic title="Total Metrics" value={totalCount} prefix={<BarChartOutlined />} /></Card></Col>
        <Col span={6}><Card><Statistic title="CPU Average" value={cpuAvg} suffix="%" /></Card></Col>
        <Col span={6}><Card><Statistic title="Memory Average" value={memAvg} suffix="%" /></Card></Col>
        <Col span={6}><Card><Statistic title="Disk Average" value={summary.disk_avg || 0} suffix="%" /></Card></Col>
      </Row>
      <Row gutter={[16, 16]} className="chart-row">
        <Col span={24}>
          <Card title="System Metrics" extra={
            <Space>
              <Button type="primary" icon={<ReloadOutlined />} onClick={fetchMetrics} loading={loading}>Refresh</Button>
            </Space>
          }>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip /><Legend />
                <Line type="monotone" dataKey="cpu" stroke="#8884d8" name="CPU (%)" />
                <Line type="monotone" dataKey="memory" stroke="#82ca9d" name="Memory (%)" />
                <Line type="monotone" dataKey="disk" stroke="#ffc658" name="Disk (%)" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
      <Row gutter={[16, 16]} className="table-row">
        <Col span={24}>
          <Card title="Recent Metrics">
            <Table columns={columns} dataSource={chartData} rowKey={(r, i) => (r.timestamp || '') + i} pagination={{ pageSize: 10 }} loading={loading} />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
