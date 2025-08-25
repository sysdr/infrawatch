import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Button, Space, Alert } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ReloadOutlined, DatabaseOutlined, BarChartOutlined, WifiOutlined, WifiOutlined as WifiDisconnectedIcon } from '@ant-design/icons';
import webSocketService from '../services/websocket';
import './Dashboard.css';

const Dashboard = () => {
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [wsError, setWsError] = useState(null);

  const sampleData = [
    { timestamp: '2024-01-01 00:00', cpu: 45, memory: 60, disk: 30 },
    { timestamp: '2024-01-01 01:00', cpu: 52, memory: 65, disk: 32 },
    { timestamp: '2024-01-01 02:00', cpu: 48, memory: 62, disk: 31 },
    { timestamp: '2024-01-01 03:00', cpu: 55, memory: 68, disk: 33 },
    { timestamp: '2024-01-01 04:00', cpu: 50, memory: 64, disk: 31 },
  ];

  const columns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
    },
    {
      title: 'CPU (%)',
      dataIndex: 'cpu',
      key: 'cpu',
    },
    {
      title: 'Memory (%)',
      dataIndex: 'memory',
      key: 'memory',
    },
    {
      title: 'Disk (%)',
      dataIndex: 'disk',
      key: 'disk',
    },
  ];

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('http://localhost:8000/api/metrics');
      // const data = await response.json();
      // setMetrics(data);
      
      // For now, use sample data
      setMetrics(sampleData);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  // WebSocket message handler
  const handleWebSocketMessage = (data) => {
    if (data.type === 'metrics_update') {
      const newMetric = {
        timestamp: new Date(data.timestamp).toLocaleTimeString(),
        cpu: data.data.cpu_usage,
        memory: data.data.memory_usage,
        disk: data.data.disk_usage,
        network: data.data.network_io
      };
      
      setMetrics(prevMetrics => {
        const updated = [...prevMetrics, newMetric];
        // Keep only last 20 metrics to prevent memory issues
        return updated.slice(-20);
      });
    }
  };

  useEffect(() => {
    fetchMetrics();
    
    // Initialize WebSocket connection
    webSocketService.addMessageHandler(handleWebSocketMessage);
    webSocketService.connect();
    
    // Update connection status
    const checkConnection = () => {
      setWsConnected(webSocketService.isConnected);
      if (!webSocketService.isConnected) {
        setWsError('WebSocket disconnected. Attempting to reconnect...');
      } else {
        setWsError(null);
      }
    };
    
    const interval = setInterval(checkConnection, 1000);
    
    return () => {
      webSocketService.removeMessageHandler(handleWebSocketMessage);
      webSocketService.disconnect();
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1><DatabaseOutlined /> Metrics Storage Dashboard</h1>
        <p>Day 24: Real-time system metrics monitoring and storage</p>
      </div>

      {/* WebSocket Status */}
      {wsError && (
        <Alert
          message="WebSocket Connection Issue"
          description={wsError}
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}
      
      {wsConnected && (
        <Alert
          message="Real-time Updates Active"
          description="Receiving live metrics via WebSocket"
          type="success"
          icon={<WifiOutlined />}
          style={{ marginBottom: 16 }}
        />
      )}

      <Row gutter={[16, 16]} className="stats-row">
        <Col span={8}>
          <Card>
            <Statistic
              title="Total Metrics"
              value={metrics.length}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="CPU Average"
              value={metrics.length > 0 ? (metrics.reduce((sum, m) => sum + m.cpu, 0) / metrics.length).toFixed(1) : 0}
              suffix="%"
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Memory Average"
              value={metrics.length > 0 ? (metrics.reduce((sum, m) => sum + m.memory, 0) / metrics.length).toFixed(1) : 0}
              suffix="%"
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} className="chart-row">
        <Col span={24}>
          <Card title="System Metrics Over Time" extra={
            <Space>
              <Button 
                type="primary" 
                icon={<ReloadOutlined />} 
                onClick={fetchMetrics}
                loading={loading}
              >
                Refresh
              </Button>
              <Button 
                icon={wsConnected ? <WifiOutlined /> : <WifiDisconnectedIcon />}
                onClick={() => wsConnected ? webSocketService.disconnect() : webSocketService.connect()}
                type={wsConnected ? "default" : "dashed"}
              >
                {wsConnected ? "Disconnect WS" : "Connect WS"}
              </Button>
            </Space>
          }>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={metrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="cpu" stroke="#8884d8" activeDot={{ r: 8 }} />
                <Line type="monotone" dataKey="memory" stroke="#82ca9d" />
                <Line type="monotone" dataKey="disk" stroke="#ffc658" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} className="table-row">
        <Col span={24}>
          <Card title="Recent Metrics Data">
            <Table 
              columns={columns} 
              dataSource={metrics} 
              rowKey="timestamp"
              pagination={{ pageSize: 10 }}
              loading={loading}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
