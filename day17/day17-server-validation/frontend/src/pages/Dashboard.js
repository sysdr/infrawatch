import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Tag, Progress } from 'antd';
import { 
  DesktopOutlined, 
  CheckCircleOutlined, 
  ExclamationCircleOutlined,
  CloseCircleOutlined 
} from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function Dashboard() {
  const [dashboardData, setDashboardData] = useState({
    stats: { total_servers: 0, healthy: 0, degraded: 0, unhealthy: 0, unreachable: 0 },
    servers: []
  });

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/validation/health-dashboard');
      const data = await response.json();
      if (data.status === 'success' && data.dashboard) {
        // Transform the API response to match the expected structure
        setDashboardData({
          stats: {
            total_servers: data.dashboard.total_servers,
            healthy: data.dashboard.healthy_servers,
            degraded: 0, // API doesn't provide this, defaulting to 0
            unhealthy: data.dashboard.unhealthy_servers,
            unreachable: 0 // API doesn't provide this, defaulting to 0
          },
          servers: data.dashboard.servers.map(server => ({
            ...server,
            ip_address: server.ip, // Map 'ip' to 'ip_address' for consistency
            last_check: data.dashboard.last_updated * 1000, // Convert to milliseconds
            id: server.hostname // Add an id field for React keys
          }))
        });
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'green';
      case 'degraded': return 'orange';
      case 'unhealthy': return 'red';
      case 'unreachable': return 'gray';
      default: return 'blue';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return <CheckCircleOutlined style={{ color: 'green' }} />;
      case 'degraded': return <ExclamationCircleOutlined style={{ color: 'orange' }} />;
      case 'unhealthy': return <CloseCircleOutlined style={{ color: 'red' }} />;
      default: return <DesktopOutlined style={{ color: 'gray' }} />;
    }
  };

  const healthPercentage = dashboardData.stats.total_servers > 0 
    ? Math.round((dashboardData.stats.healthy / dashboardData.stats.total_servers) * 100)
    : 0;

  const columns = [
    {
      title: 'Server',
      dataIndex: 'hostname',
      key: 'hostname',
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{text}</div>
          <div style={{ color: '#666', fontSize: '12px' }}>{record.ip_address}</div>
        </div>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={getStatusColor(status)} icon={getStatusIcon(status)}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Response Time',
      dataIndex: 'response_time',
      key: 'response_time',
      render: (time) => `${Math.round(time || 0)}ms`,
    },
    {
      title: 'Last Check',
      dataIndex: 'last_check',
      key: 'last_check',
      render: (time) => time ? new Date(time).toLocaleTimeString() : 'Never',
    },
  ];

  // Mock data for chart
  const chartData = [
    { time: '00:00', healthy: 8, degraded: 1, unhealthy: 0 },
    { time: '04:00', healthy: 7, degraded: 2, unhealthy: 0 },
    { time: '08:00', healthy: 9, degraded: 0, unhealthy: 0 },
    { time: '12:00', healthy: 8, degraded: 1, unhealthy: 0 },
    { time: '16:00', healthy: 9, degraded: 0, unhealthy: 0 },
    { time: '20:00', healthy: 8, degraded: 1, unhealthy: 0 },
  ];

  return (
    <div>
      <h1>Infrastructure Health Dashboard</h1>
      
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Servers"
              value={dashboardData.stats.total_servers}
              prefix={<DesktopOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Healthy"
              value={dashboardData.stats.healthy}
              valueStyle={{ color: '#3f8600' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Issues"
              value={dashboardData.stats.degraded + dashboardData.stats.unhealthy}
              valueStyle={{ color: '#cf1322' }}
              prefix={<ExclamationCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ marginBottom: 8 }}>Health Score</div>
              <Progress
                type="circle"
                percent={healthPercentage}
                strokeColor={{
                  '0%': '#ff4d4f',
                  '50%': '#faad14',
                  '100%': '#52c41a',
                }}
                size={80}
              />
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={16}>
          <Card title="Server Status">
            <Table 
              dataSource={dashboardData.servers} 
              columns={columns} 
              rowKey="id"
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="24-Hour Health Trend">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="healthy" stroke="#52c41a" strokeWidth={2} />
                <Line type="monotone" dataKey="degraded" stroke="#faad14" strokeWidth={2} />
                <Line type="monotone" dataKey="unhealthy" stroke="#ff4d4f" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default Dashboard;
