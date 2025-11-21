import React, { useState, useEffect, useCallback } from 'react';
import { Layout, Card, Row, Col, Statistic, Button, Input, Select, notification } from 'antd';
import { 
  UserOutlined, 
  ThunderboltOutlined, 
  ClockCircleOutlined, 
  DatabaseOutlined,
  BarChartOutlined
} from '@ant-design/icons';
import MetricsChart from './components/MetricsChart';
import NotificationPanel from './components/NotificationPanel';
import ConnectionTest from './components/ConnectionTest';
import './App.css';

const { Header, Content } = Layout;
const { Option } = Select;

function App() {
  const [metrics, setMetrics] = useState({
    active_connections: 0,
    memory_usage_mb: 0,
    messages_per_second: 0,
    average_latency_ms: 0,
    queue_depth: 0,
    compression_ratio: 0
  });
  const [metricsHistory, setMetricsHistory] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    // Fetch metrics every second
    const interval = setInterval(async () => {
      try {
        const response = await fetch('http://localhost:8000/api/metrics/current');
        const data = await response.json();
        setMetrics(data);
        
        // Update history
        setMetricsHistory(prev => {
          const newHistory = [...prev, data];
          return newHistory.slice(-60); // Keep last 60 seconds
        });
      } catch (error) {
        console.error('Error fetching metrics:', error);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Header style={{ background: '#001529', padding: '0 24px' }}>
        <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
          ⚡ Real-time Performance Dashboard
        </div>
      </Header>
      
      <Content style={{ padding: '24px' }}>
        {/* Metrics Overview */}
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col xs={24} sm={12} md={8} lg={4}>
            <Card>
              <Statistic
                title="Active Connections"
                value={metrics.active_connections || 0}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#3f8600' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={4}>
            <Card>
              <Statistic
                title="Messages/sec"
                value={metrics.messages_per_second || 0}
                prefix={<ThunderboltOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={4}>
            <Card>
              <Statistic
                title="Avg Latency"
                value={(metrics.average_latency_ms || 0).toFixed(2)}
                suffix="ms"
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: metrics.average_latency_ms > 100 ? '#cf1322' : '#3f8600' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={4}>
            <Card>
              <Statistic
                title="Queue Depth"
                value={metrics.queue_depth || 0}
                prefix={<DatabaseOutlined />}
                valueStyle={{ color: metrics.queue_depth > 1000 ? '#cf1322' : '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={4}>
            <Card>
              <Statistic
                title="Memory Usage"
                value={(metrics.memory_usage_mb || 0).toFixed(0)}
                suffix="MB"
                prefix={<BarChartOutlined />}
                valueStyle={{ color: metrics.memory_usage_mb > 2000 ? '#cf1322' : '#3f8600' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={4}>
            <Card>
              <Statistic
                title="Compression"
                value={((metrics.compression_ratio || 0) * 100).toFixed(1)}
                suffix="%"
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
        </Row>

        {/* Charts */}
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col xs={24} lg={12}>
            <MetricsChart 
              data={metricsHistory} 
              title="Performance Metrics"
              dataKeys={['messages_per_second', 'average_latency_ms']}
            />
          </Col>
          <Col xs={24} lg={12}>
            <MetricsChart 
              data={metricsHistory} 
              title="Resource Usage"
              dataKeys={['memory_usage_mb', 'active_connections', 'queue_depth']}
            />
          </Col>
        </Row>

        {/* Connection Test */}
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <ConnectionTest />
          </Col>
          <Col xs={24} lg={12}>
            <NotificationPanel />
          </Col>
        </Row>
      </Content>
    </Layout>
  );
}

export default App;
