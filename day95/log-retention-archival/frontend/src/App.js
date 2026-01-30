import React, { useState, useEffect } from 'react';
import { Layout, Menu, Card, Row, Col, Statistic, Table, Button, Tag, Progress, message } from 'antd';
import { DatabaseOutlined, CloudServerOutlined, SafetyOutlined, DollarOutlined, SyncOutlined } from '@ant-design/icons';
import axios from 'axios';
import { BarChart, Bar, PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

const { Header, Content, Sider } = Layout;

const API_BASE = 'http://localhost:8000';

const COLORS = ['#52c41a', '#1890ff', '#faad14', '#f5222d'];

function App() {
  const [activeMenu, setActiveMenu] = useState('overview');
  const [stats, setStats] = useState({});
  const [costs, setCosts] = useState({});
  const [logs, setLogs] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, costsRes, logsRes, jobsRes, policiesRes, recsRes] = await Promise.all([
        axios.get(`${API_BASE}/logs/stats`),
        axios.get(`${API_BASE}/costs`),
        axios.get(`${API_BASE}/logs?limit=50`),
        axios.get(`${API_BASE}/jobs?limit=20`),
        axios.get(`${API_BASE}/policies`),
        axios.get(`${API_BASE}/costs/recommendations`)
      ]);

      setStats(statsRes.data);
      setCosts(costsRes.data);
      setLogs(logsRes.data);
      setJobs(jobsRes.data);
      setPolicies(policiesRes.data);
      setRecommendations(recsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const handleGenerateLogs = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/logs/generate?count=100`);
      message.success('Generated 100 sample logs');
      await fetchData();
    } catch (error) {
      message.error('Failed to generate logs');
    }
    setLoading(false);
  };

  const handleEvaluateRetention = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/retention/evaluate`);
      message.success(`Found ${response.data.transitions_found} logs to transition`);
      await fetchData();
    } catch (error) {
      message.error('Failed to evaluate retention');
    }
    setLoading(false);
  };

  const renderOverview = () => {
    const tierData = [
      { name: 'Hot', value: stats.hot?.count || 0, cost: costs.tiers?.hot?.total_cost || 0 },
      { name: 'Warm', value: stats.warm?.count || 0, cost: costs.tiers?.warm?.total_cost || 0 },
      { name: 'Cold', value: stats.cold?.count || 0, cost: costs.tiers?.cold?.total_cost || 0 }
    ];
    const totalLogs = (stats.hot?.count || 0) + (stats.warm?.count || 0) + (stats.cold?.count || 0);
    const showEmptyHint = totalLogs === 0;

    return (
      <div>
        {showEmptyHint && (
          <div style={{ marginBottom: 16, padding: 12, background: '#e6f7ff', border: '1px solid #91d5ff', borderRadius: 8 }}>
            <strong>No data yet.</strong> Click &quot;Generate Sample Logs&quot; below to populate the dashboard with demo data. Metrics will update automatically.
          </div>
        )}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="Hot Storage"
                value={stats.hot?.count || 0}
                prefix={<DatabaseOutlined style={{ color: '#52c41a' }} />}
                suffix="logs"
              />
              <div style={{ marginTop: 8, fontSize: 12, color: '#888' }}>
                {stats.hot?.total_size_mb || 0} MB
              </div>
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="Warm Storage"
                value={stats.warm?.count || 0}
                prefix={<CloudServerOutlined style={{ color: '#1890ff' }} />}
                suffix="logs"
              />
              <div style={{ marginTop: 8, fontSize: 12, color: '#888' }}>
                {stats.warm?.total_size_mb || 0} MB
              </div>
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="Cold Storage"
                value={stats.cold?.count || 0}
                prefix={<SafetyOutlined style={{ color: '#faad14' }} />}
                suffix="logs"
              />
              <div style={{ marginTop: 8, fontSize: 12, color: '#888' }}>
                {stats.cold?.total_size_mb || 0} MB
              </div>
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="Total Cost"
                value={costs.total_cost || 0}
                prefix={<DollarOutlined style={{ color: '#f5222d' }} />}
                precision={2}
                suffix="/ month"
              />
              <div style={{ marginTop: 8, fontSize: 12, color: '#888' }}>
                {costs.total_size_gb || 0} GB total
              </div>
            </Card>
          </Col>
        </Row>

        <Row gutter={[16, 16]}>
          <Col span={12}>
            <Card title="Storage Distribution" extra={<Button icon={<SyncOutlined />} onClick={fetchData}>Refresh</Button>}>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={tierData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {tierData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="Cost by Tier">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={tierData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="cost" fill="#1890ff" name="Monthly Cost ($)" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </Col>
        </Row>

        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col span={24}>
            <Card 
              title="Quick Actions"
              extra={
                <div>
                  <Button 
                    type="primary" 
                    onClick={handleGenerateLogs} 
                    loading={loading}
                    style={{ marginRight: 8 }}
                  >
                    Generate Sample Logs
                  </Button>
                  <Button 
                    onClick={handleEvaluateRetention} 
                    loading={loading}
                  >
                    Evaluate Retention
                  </Button>
                </div>
              }
            >
              <p>Use these actions to populate the system with data and trigger retention evaluation.</p>
            </Card>
          </Col>
        </Row>
      </div>
    );
  };

  const renderLogs = () => {
    const columns = [
      {
        title: 'Source',
        dataIndex: 'source',
        key: 'source',
        width: 150
      },
      {
        title: 'Level',
        dataIndex: 'level',
        key: 'level',
        width: 100,
        render: (level) => {
          const colors = {
            error: 'red',
            warning: 'orange',
            info: 'blue',
            debug: 'green'
          };
          return <Tag color={colors[level]}>{level.toUpperCase()}</Tag>;
        }
      },
      {
        title: 'Message',
        dataIndex: 'message',
        key: 'message',
        ellipsis: true
      },
      {
        title: 'Storage Tier',
        dataIndex: 'storage_tier',
        key: 'storage_tier',
        width: 120,
        render: (tier) => {
          const colors = {
            hot: 'green',
            warm: 'blue',
            cold: 'orange'
          };
          return <Tag color={colors[tier]}>{tier.toUpperCase()}</Tag>;
        }
      },
      {
        title: 'Compression',
        key: 'compression',
        width: 120,
        render: (_, record) => (
          record.compression_ratio ? 
          <Progress 
            percent={Math.round((1 - record.compression_ratio) * 100)} 
            size="small" 
            status="active"
          /> : '-'
        )
      },
      {
        title: 'Timestamp',
        dataIndex: 'timestamp',
        key: 'timestamp',
        width: 180,
        render: (timestamp) => new Date(timestamp).toLocaleString()
      }
    ];

    return (
      <Card title="Log Entries" extra={<Button icon={<SyncOutlined />} onClick={fetchData}>Refresh</Button>}>
        <Table 
          columns={columns} 
          dataSource={logs} 
          rowKey="id"
          pagination={{ pageSize: 20 }}
          size="small"
        />
      </Card>
    );
  };

  const renderJobs = () => {
    const columns = [
      {
        title: 'ID',
        dataIndex: 'id',
        key: 'id',
        width: 60
      },
      {
        title: 'Type',
        dataIndex: 'job_type',
        key: 'job_type',
        width: 100
      },
      {
        title: 'Status',
        dataIndex: 'status',
        key: 'status',
        width: 100,
        render: (status) => {
          const colors = {
            pending: 'default',
            running: 'processing',
            completed: 'success',
            failed: 'error'
          };
          return <Tag color={colors[status]}>{status.toUpperCase()}</Tag>;
        }
      },
      {
        title: 'Transition',
        key: 'transition',
        width: 150,
        render: (_, record) => (
          record.source_tier && record.target_tier ?
          `${record.source_tier} → ${record.target_tier}` : '-'
        )
      },
      {
        title: 'Logs',
        dataIndex: 'log_count',
        key: 'log_count',
        width: 80
      },
      {
        title: 'Data Size',
        dataIndex: 'data_size_mb',
        key: 'data_size_mb',
        width: 100,
        render: (size) => `${size} MB`
      },
      {
        title: 'Compressed',
        dataIndex: 'compressed_size_mb',
        key: 'compressed_size_mb',
        width: 120,
        render: (size) => `${size} MB`
      },
      {
        title: 'Started',
        dataIndex: 'started_at',
        key: 'started_at',
        width: 180,
        render: (timestamp) => timestamp ? new Date(timestamp).toLocaleString() : '-'
      }
    ];

    return (
      <Card title="Archival Jobs" extra={<Button icon={<SyncOutlined />} onClick={fetchData}>Refresh</Button>}>
        <Table 
          columns={columns} 
          dataSource={jobs} 
          rowKey="id"
          pagination={{ pageSize: 15 }}
          size="small"
        />
      </Card>
    );
  };

  const renderPolicies = () => {
    const columns = [
      {
        title: 'Name',
        dataIndex: 'name',
        key: 'name',
        width: 200
      },
      {
        title: 'Pattern',
        dataIndex: 'log_source_pattern',
        key: 'log_source_pattern',
        width: 150
      },
      {
        title: 'Hot (days)',
        dataIndex: 'hot_retention_days',
        key: 'hot_retention_days',
        width: 100
      },
      {
        title: 'Warm (days)',
        dataIndex: 'warm_retention_days',
        key: 'warm_retention_days',
        width: 100
      },
      {
        title: 'Cold (days)',
        dataIndex: 'cold_retention_days',
        key: 'cold_retention_days',
        width: 100
      },
      {
        title: 'Compliance',
        dataIndex: 'compliance_frameworks',
        key: 'compliance_frameworks',
        render: (frameworks) => (
          frameworks?.map(f => <Tag key={f} color="blue">{f}</Tag>)
        )
      },
      {
        title: 'Auto Delete',
        dataIndex: 'auto_delete',
        key: 'auto_delete',
        width: 100,
        render: (autoDelete) => (
          <Tag color={autoDelete ? 'red' : 'green'}>
            {autoDelete ? 'YES' : 'NO'}
          </Tag>
        )
      },
      {
        title: 'Status',
        dataIndex: 'enabled',
        key: 'enabled',
        width: 80,
        render: (enabled) => (
          <Tag color={enabled ? 'success' : 'default'}>
            {enabled ? 'ACTIVE' : 'DISABLED'}
          </Tag>
        )
      }
    ];

    return (
      <Card title="Retention Policies" extra={<Button icon={<SyncOutlined />} onClick={fetchData}>Refresh</Button>}>
        <Table 
          columns={columns} 
          dataSource={policies} 
          rowKey="id"
          pagination={false}
          size="small"
        />
      </Card>
    );
  };

  const renderCosts = () => {
    const tierCosts = costs.tiers ? [
      { 
        tier: 'Hot', 
        logs: costs.tiers.hot?.log_count || 0,
        size: costs.tiers.hot?.total_size_gb || 0,
        cost: costs.tiers.hot?.total_cost || 0,
        rate: costs.tiers.hot?.cost_per_gb || 0
      },
      { 
        tier: 'Warm', 
        logs: costs.tiers.warm?.log_count || 0,
        size: costs.tiers.warm?.total_size_gb || 0,
        cost: costs.tiers.warm?.total_cost || 0,
        rate: costs.tiers.warm?.cost_per_gb || 0
      },
      { 
        tier: 'Cold', 
        logs: costs.tiers.cold?.log_count || 0,
        size: costs.tiers.cold?.total_size_gb || 0,
        cost: costs.tiers.cold?.total_cost || 0,
        rate: costs.tiers.cold?.cost_per_gb || 0
      }
    ] : [];

    const columns = [
      {
        title: 'Tier',
        dataIndex: 'tier',
        key: 'tier',
        render: (tier) => {
          const colors = { Hot: 'green', Warm: 'blue', Cold: 'orange' };
          return <Tag color={colors[tier]}>{tier}</Tag>;
        }
      },
      {
        title: 'Log Count',
        dataIndex: 'logs',
        key: 'logs'
      },
      {
        title: 'Storage (GB)',
        dataIndex: 'size',
        key: 'size',
        render: (size) => size.toFixed(2)
      },
      {
        title: 'Rate ($/GB)',
        dataIndex: 'rate',
        key: 'rate',
        render: (rate) => `$${rate.toFixed(3)}`
      },
      {
        title: 'Monthly Cost',
        dataIndex: 'cost',
        key: 'cost',
        render: (cost) => `$${cost.toFixed(2)}`
      }
    ];

    const recColumns = [
      {
        title: 'Log Source',
        dataIndex: 'source',
        key: 'source'
      },
      {
        title: 'Age (days)',
        dataIndex: 'age_days',
        key: 'age_days'
      },
      {
        title: 'Current Tier',
        dataIndex: 'current_tier',
        key: 'current_tier',
        render: (tier) => <Tag color="green">{tier.toUpperCase()}</Tag>
      },
      {
        title: 'Recommended',
        dataIndex: 'recommended_tier',
        key: 'recommended_tier',
        render: (tier) => <Tag color="blue">{tier.toUpperCase()}</Tag>
      },
      {
        title: 'Savings',
        dataIndex: 'potential_savings',
        key: 'potential_savings',
        render: (savings) => `$${savings.toFixed(4)}/mo`
      }
    ];

    return (
      <div>
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card title="Cost Breakdown">
              <Table 
                columns={columns} 
                dataSource={tierCosts} 
                rowKey="tier"
                pagination={false}
                summary={(pageData) => {
                  const totalCost = pageData.reduce((sum, row) => sum + row.cost, 0);
                  const totalSize = pageData.reduce((sum, row) => sum + row.size, 0);
                  return (
                    <Table.Summary.Row style={{ fontWeight: 'bold', background: '#fafafa' }}>
                      <Table.Summary.Cell>Total</Table.Summary.Cell>
                      <Table.Summary.Cell>-</Table.Summary.Cell>
                      <Table.Summary.Cell>{totalSize.toFixed(2)} GB</Table.Summary.Cell>
                      <Table.Summary.Cell>-</Table.Summary.Cell>
                      <Table.Summary.Cell>${totalCost.toFixed(2)}</Table.Summary.Cell>
                    </Table.Summary.Row>
                  );
                }}
              />
            </Card>
          </Col>
        </Row>

        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col span={24}>
            <Card title={`Cost Optimization Recommendations (${recommendations.length})`}>
              {recommendations.length > 0 ? (
                <Table 
                  columns={recColumns} 
                  dataSource={recommendations} 
                  rowKey="log_id"
                  pagination={{ pageSize: 10 }}
                  size="small"
                />
              ) : (
                <div style={{ textAlign: 'center', padding: 40, color: '#888' }}>
                  No optimization recommendations at this time
                </div>
              )}
            </Card>
          </Col>
        </Row>
      </div>
    );
  };

  const renderContent = () => {
    switch (activeMenu) {
      case 'overview':
        return renderOverview();
      case 'logs':
        return renderLogs();
      case 'jobs':
        return renderJobs();
      case 'policies':
        return renderPolicies();
      case 'costs':
        return renderCosts();
      default:
        return renderOverview();
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#001529', padding: '0 24px' }}>
        <div style={{ color: 'white', fontSize: 20, fontWeight: 'bold' }}>
          <DatabaseOutlined style={{ marginRight: 12 }} />
          Log Retention & Archival System
        </div>
      </Header>
      <Layout>
        <Sider width={250} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            selectedKeys={[activeMenu]}
            onClick={(e) => setActiveMenu(e.key)}
            style={{ height: '100%', borderRight: 0 }}
            items={[
              {
                key: 'overview',
                icon: <DatabaseOutlined />,
                label: 'Overview'
              },
              {
                key: 'logs',
                icon: <DatabaseOutlined />,
                label: 'Log Entries'
              },
              {
                key: 'jobs',
                icon: <SyncOutlined />,
                label: 'Archival Jobs'
              },
              {
                key: 'policies',
                icon: <SafetyOutlined />,
                label: 'Retention Policies'
              },
              {
                key: 'costs',
                icon: <DollarOutlined />,
                label: 'Cost Analysis'
              }
            ]}
          />
        </Sider>
        <Layout style={{ padding: '24px' }}>
          <Content
            style={{
              padding: 24,
              margin: 0,
              minHeight: 280,
              background: '#fff'
            }}
          >
            {renderContent()}
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
}

export default App;
