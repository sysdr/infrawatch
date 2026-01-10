import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Table, Statistic, Tag, message } from 'antd';
import { BarChartOutlined, UserOutlined, TeamOutlined, SafetyOutlined } from '@ant-design/icons';
import { activityAPI, statsAPI } from '../services/api';
import dayjs from 'dayjs';

function ActivityDashboard() {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({
    total_users: 0,
    active_users: 0,
    active_teams: 0,
    total_permissions: 0,
    recent_activities: 0,
  });

  useEffect(() => {
    fetchActivities();
    fetchStats();
    // Refresh stats every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await statsAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
      message.error('Failed to fetch dashboard statistics');
    }
  };

  const fetchActivities = async () => {
    setLoading(true);
    try {
      const response = await activityAPI.getRecent({ hours: 24, limit: 50 });
      setActivities(response.data.activities);
    } catch (error) {
      console.error('Failed to fetch activities');
    }
    setLoading(false);
  };

  const columns = [
    {
      title: 'Action',
      dataIndex: 'action',
      key: 'action',
      render: (action) => <Tag color="blue">{action}</Tag>,
    },
    {
      title: 'Resource Type',
      dataIndex: 'resource_type',
      key: 'resource_type',
    },
    {
      title: 'Resource ID',
      dataIndex: 'resource_id',
      key: 'resource_id',
      render: (id) => id ? id.substring(0, 8) + '...' : '-',
    },
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp) => dayjs(timestamp).format('YYYY-MM-DD HH:mm:ss'),
    },
  ];

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Total Users"
              value={stats.total_users || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Active Teams"
              value={stats.active_teams || 0}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Total Permissions"
              value={stats.total_permissions || 0}
              prefix={<SafetyOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      <Card title={<><BarChartOutlined /> Recent Activity (Last 24 Hours)</>}>
        <Table
          columns={columns}
          dataSource={activities}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
}

export default ActivityDashboard;
