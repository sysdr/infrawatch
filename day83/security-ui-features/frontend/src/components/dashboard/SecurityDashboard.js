import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Alert, Spin, Typography } from 'antd';
import { 
  WarningOutlined, 
  CheckCircleOutlined, 
  ClockCircleOutlined,
  TrophyOutlined 
} from '@ant-design/icons';
import { 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { securityApi } from '../../services/api';
import { useWebSocket } from '../../hooks/useWebSocket';

const { Title } = Typography;

const COLORS = {
  CRITICAL: '#f5222d',
  HIGH: '#fa8c16',
  MEDIUM: '#faad14',
  LOW: '#52c41a'
};

function SecurityDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [distribution, setDistribution] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);
  const { events, isConnected } = useWebSocket();

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      const [metricsRes, distRes, timelineRes] = await Promise.all([
        securityApi.getDashboardMetrics(),
        securityApi.getThreatDistribution(),
        securityApi.getTimeline(24)
      ]);
      
      setMetrics(metricsRes.data);
      setDistribution(distRes.data);
      setTimeline(timelineRes.data.timeline);
      setLoading(false);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2} style={{ margin: 0 }}>Security Dashboard</Title>
        <Alert 
          message={isConnected ? "Real-time monitoring active" : "Connecting..."} 
          type={isConnected ? "success" : "warning"}
          showIcon
        />
      </div>

      {/* Metrics Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Active Threats"
              value={metrics?.active_threats || 0}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#f5222d' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Events (Last Hour)"
              value={metrics?.events_last_hour || 0}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Avg Threat Score"
              value={metrics?.avg_threat_score || 0}
              suffix="/ 100"
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="System Status"
              value="Operational"
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts Row */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={16}>
          <Card title="24-Hour Security Timeline">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={timeline}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleString()}
                />
                <Legend />
                <Line type="monotone" dataKey="critical" stroke="#f5222d" name="Critical" />
                <Line type="monotone" dataKey="high" stroke="#fa8c16" name="High" />
                <Line type="monotone" dataKey="medium" stroke="#faad14" name="Medium" />
                <Line type="monotone" dataKey="low" stroke="#52c41a" name="Low" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Severity Distribution">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={distribution?.severity_distribution || []}
                  dataKey="count"
                  nameKey="severity"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {(distribution?.severity_distribution || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[entry.severity]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Top Event Types */}
      <Row gutter={[16, 16]}>
        <Col xs={24}>
          <Card title="Top Event Types">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={distribution?.type_distribution || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="event_type" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#1890ff" name="Event Count" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Real-time Event Stream */}
      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        <Col xs={24}>
          <Card title={`Real-time Event Stream (${events.length} events)`}>
            <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
              {events.slice(0, 50).map((event, index) => (
                <div 
                  key={index}
                  className={`event-item ${event.severity}`}
                  style={{ marginBottom: '8px' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <span className={`severity-badge severity-${event.severity}`}>
                        {event.severity}
                      </span>
                      <span style={{ marginLeft: '12px', fontWeight: 500 }}>
                        {event.event_type}
                      </span>
                      <span style={{ marginLeft: '12px', color: '#888' }}>
                        {event.description}
                      </span>
                    </div>
                    <div style={{ color: '#888', fontSize: '12px' }}>
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                  <div style={{ marginTop: '4px', fontSize: '12px', color: '#666' }}>
                    User: {event.user_id} | IP: {event.ip_address} | Score: {event.threat_score}
                  </div>
                </div>
              ))}
              {events.length === 0 && (
                <div style={{ textAlign: 'center', padding: '40px', color: '#888' }}>
                  Waiting for security events...
                </div>
              )}
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default SecurityDashboard;
