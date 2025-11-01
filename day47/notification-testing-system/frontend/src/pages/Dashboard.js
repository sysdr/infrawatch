import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Alert, Progress, Badge } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { useQuery } from 'react-query';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const Dashboard = () => {
  const [realTimeMetrics, setRealTimeMetrics] = useState(null);
  
  // Query for current metrics
  const { data: currentMetrics, isLoading } = useQuery(
    'currentMetrics',
    () => axios.get(`${API_BASE}/metrics/current`).then(res => res.data),
    { refetchInterval: 2000 }
  );

  // Query for health status
  const { data: healthStatus } = useQuery(
    'healthStatus',
    () => axios.get(`${API_BASE}/health`).then(res => res.data),
    { refetchInterval: 1000 }
  );

  // Query for circuit breaker status
  const { data: circuitStatus } = useQuery(
    'circuitStatus',
    () => axios.get(`${API_BASE}/circuit-breakers`).then(res => res.data),
    { refetchInterval: 2000 }
  );

  // WebSocket for real-time updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/metrics');

    ws.onopen = () => {
      console.log('Connected to real-time metrics');
      // Send initial message to keep connection alive
      ws.send(JSON.stringify({ type: 'subscribe' }));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setRealTimeMetrics(data);
      } catch (e) {
        console.error('Error parsing WebSocket message:', e);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  if (isLoading) {
    return <div>Loading dashboard...</div>;
  }

  const getHealthColor = (health) => {
    if (health > 0.9) return '#52c41a';
    if (health > 0.7) return '#faad14';
    return '#f5222d';
  };

  const getStatusBadge = (status) => {
    const colors = {
      healthy: 'success',
      degraded: 'warning',
      circuit_open: 'error',
      closed: 'success',
      open: 'error'
    };
    return <Badge status={colors[status] || 'default'} text={status} />;
  };

  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ marginBottom: '24px' }}>Notification System Dashboard</h1>
      
      {/* System Health Overview */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Overall Health"
              value={(healthStatus?.details?.overall_health || 0) * 100}
              precision={1}
              suffix="%"
              valueStyle={{ color: getHealthColor(healthStatus?.details?.overall_health || 0) }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Requests"
              value={currentMetrics?.notifications?.total_sent || 0}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Success Rate"
              value={currentMetrics?.notifications?.total_sent > 0 ? 
                ((currentMetrics.notifications.total_sent - currentMetrics.notifications.total_failed) / currentMetrics.notifications.total_sent * 100) : 100}
              precision={1}
              suffix="%"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Avg Response Time"
              value={currentMetrics?.performance?.avg_response_time || 0}
              precision={0}
              suffix="ms"
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* System Status Alerts */}
      {healthStatus?.status === 'degraded' && (
        <Alert
          message="System Degraded"
          description="Some notification channels are experiencing issues"
          type="warning"
          style={{ marginBottom: '24px' }}
          showIcon
        />
      )}

      {/* Channel Health */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <Card title="Channel Health Status">
            <Row gutter={[16, 16]}>
              {healthStatus?.details?.channels && Object.entries(healthStatus.details.channels).map(([channel, data]) => (
                <Col span={6} key={channel}>
                  <Card size="small">
                    <div style={{ textAlign: 'center' }}>
                      <h4 style={{ textTransform: 'capitalize' }}>{channel}</h4>
                      <Progress
                        type="circle"
                        percent={Math.round(data.success_rate * 100)}
                        format={percent => `${percent}%`}
                        strokeColor={getHealthColor(data.success_rate)}
                        size={80}
                      />
                      <div style={{ marginTop: '8px' }}>
                        <small>
                          {data.total_attempts} attempts<br/>
                          {Math.round(data.avg_latency_ms)}ms avg
                        </small>
                      </div>
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Circuit Breaker Status */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <Card title="Circuit Breaker Status">
            <Row gutter={[16, 16]}>
              {circuitStatus && Object.entries(circuitStatus).map(([channel, data]) => (
                <Col span={6} key={channel}>
                  <Card size="small">
                    <div style={{ textAlign: 'center' }}>
                      <h4 style={{ textTransform: 'capitalize' }}>{channel}</h4>
                      {getStatusBadge(data.state)}
                      <div style={{ marginTop: '8px' }}>
                        <small>
                          Error Rate: {(data.error_rate * 100).toFixed(1)}%<br/>
                          Recent: {data.recent_errors}/{data.recent_total}
                        </small>
                      </div>
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Performance Metrics */}
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card title="System Performance">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={realTimeMetrics ? [realTimeMetrics] : []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="system.cpu_percent" stroke="#8884d8" name="CPU %" />
                <Line type="monotone" dataKey="system.memory_percent" stroke="#82ca9d" name="Memory %" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Notification Volume by Channel">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={[
                { channel: 'Email', sent: currentMetrics?.notifications?.email_sent || 0 },
                { channel: 'SMS', sent: currentMetrics?.notifications?.sms_sent || 0 },
                { channel: 'Push', sent: currentMetrics?.notifications?.push_sent || 0 },
                { channel: 'Webhook', sent: currentMetrics?.notifications?.webhook_sent || 0 }
              ]}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="channel" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="sent" fill="#1890ff" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
