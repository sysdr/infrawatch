import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Select, Spin } from 'antd';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { analyticsService } from '../services/api';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';

const { Option } = Select;

function Analytics() {
  const [stats, setStats] = useState([]);
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState(24);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const response = await analyticsService.getRateLimitStats(timeRange);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const totalRequests = stats.reduce((sum, s) => sum + s.total_requests, 0);
  const totalRateLimited = stats.reduce((sum, s) => sum + s.rate_limited_requests, 0);
  const avgResponseTime = stats.length > 0 
    ? stats.reduce((sum, s) => sum + s.avg_response_time, 0) / stats.length 
    : 0;

  const rateLimitPercentage = totalRequests > 0 
    ? ((totalRateLimited / totalRequests) * 100).toFixed(2)
    : 0;

  const barChartData = stats.map(s => ({
    name: s.api_key_id.substring(0, 8),
    requests: s.total_requests,
    rateLimited: s.rate_limited_requests
  }));

  const pieChartData = stats.map(s => ({
    name: s.api_key_id.substring(0, 8),
    value: s.total_requests
  }));

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '50px' }}><Spin size="large" /></div>;
  }

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Analytics Dashboard</h2>
        <Select 
          value={timeRange} 
          onChange={setTimeRange}
          style={{ width: 150 }}
        >
          <Option value={1}>Last Hour</Option>
          <Option value={24}>Last 24 Hours</Option>
          <Option value={168}>Last Week</Option>
          <Option value={720}>Last Month</Option>
        </Select>
      </div>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Requests"
              value={totalRequests}
              valueStyle={{ color: '#3f8600' }}
              prefix={<ArrowUpOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Rate Limited"
              value={totalRateLimited}
              valueStyle={{ color: '#cf1322' }}
              suffix={`/ ${rateLimitPercentage}%`}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Avg Response Time"
              value={avgResponseTime.toFixed(2)}
              suffix="ms"
              valueStyle={{ 
                color: avgResponseTime < 100 ? '#3f8600' : avgResponseTime < 500 ? '#d48806' : '#cf1322' 
              }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Active API Keys"
              value={stats.length}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={16}>
          <Card title="Requests by API Key">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={barChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="requests" fill="#1890ff" name="Total Requests" />
                <Bar dataKey="rateLimited" fill="#ff4d4f" name="Rate Limited" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col span={8}>
          <Card title="Request Distribution">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      <Card title="Performance Metrics by API Key">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={stats.map(s => ({
            name: s.api_key_id.substring(0, 8),
            responseTime: s.avg_response_time
          }))}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="responseTime" 
              stroke="#8884d8" 
              name="Avg Response Time (ms)"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </Card>
    </div>
  );
}

export default Analytics;
