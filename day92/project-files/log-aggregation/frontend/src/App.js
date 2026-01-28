import React, { useState, useEffect, useCallback } from 'react';
import { Layout, Card, Row, Col, Table, Tag, Button, Select, Input, Statistic, Switch, Modal, Form, notification } from 'antd';
import { ReloadOutlined, SearchOutlined, SettingOutlined, DatabaseOutlined, CloudUploadOutlined } from '@ant-design/icons';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import dayjs from 'dayjs';
import './App.css';

const { Header, Content } = Layout;
const { Option } = Select;

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const COLORS = ['#52c41a', '#faad14', '#ff4d4f', '#1890ff', '#722ed1'];

function App() {
  const [logs, setLogs] = useState([]);
  const [parsers, setParsers] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({ service: null, level: null });
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [parserModalVisible, setParserModalVisible] = useState(false);

  // Fetch logs
  const fetchLogs = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (filters.service) params.append('service', filters.service);
      if (filters.level) params.append('level', filters.level);
      params.append('limit', '100');
      
      const response = await axios.get(`${API_BASE}/api/logs?${params.toString()}`);
      setLogs(response.data.logs);
    } catch (error) {
      console.error('Error fetching logs:', error);
    }
  }, [filters]);

  // Fetch parsers
  const fetchParsers = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/parsers`);
      setParsers(response.data.parsers);
    } catch (error) {
      console.error('Error fetching parsers:', error);
    }
  };

  // Fetch metrics
  const fetchMetrics = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/metrics/summary`);
      setMetrics(response.data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  // Real-time updates: 5s polling plus WebSocket when backend is up (ws errors suppressed)
  // Initial load and auto-refresh
  useEffect(() => {
    fetchLogs();
    fetchParsers();
    fetchMetrics();
    
    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchLogs();
        fetchMetrics();
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, fetchLogs]);

  // WebSocket for live logs: connect to backend /ws/logs; errors suppressed to avoid console noise when backend is down.
  useEffect(() => {
    const base = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    const wsUrl = base.replace(/^http/, 'ws').replace(/\/$/, '') + '/ws/logs';
    let ws;
    try {
      ws = new WebSocket(wsUrl);
      ws.onerror = () => {};
      ws.onclose = () => {};
      ws.onmessage = () => { fetchLogs(); fetchMetrics(); };
    } catch (_) {}
    return () => { try { if (ws) ws.close(); } catch (_) {} };
  }, [fetchLogs, fetchMetrics]);

  // Table columns
  const columns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (text) => dayjs(text).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: 'Level',
      dataIndex: 'level',
      key: 'level',
      width: 80,
      render: (level) => {
        const colors = {
          ERROR: 'red',
          WARN: 'orange',
          INFO: 'blue',
          DEBUG: 'default',
        };
        return <Tag color={colors[level] || 'default'}>{level}</Tag>;
      },
    },
    {
      title: 'Service',
      dataIndex: 'service',
      key: 'service',
      width: 120,
    },
    {
      title: 'Message',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
    },
    {
      title: 'Trace ID',
      dataIndex: 'trace_id',
      key: 'trace_id',
      width: 140,
      render: (text) => text ? <code>{text.substring(0, 12)}...</code> : '-',
    },
  ];

  // Parser table columns
  const parserColumns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Format',
      dataIndex: 'format_type',
      key: 'format_type',
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
    },
    {
      title: 'Status',
      dataIndex: 'enabled',
      key: 'enabled',
      render: (enabled) => <Tag color={enabled ? 'green' : 'default'}>{enabled ? 'Enabled' : 'Disabled'}</Tag>,
    },
  ];

  // Prepare chart data
  const levelData = metrics?.levels ? Object.entries(metrics.levels).map(([name, value]) => ({ name, value })) : [];
  const serviceData = metrics?.services ? Object.entries(metrics.services).map(([name, value]) => ({ name, value })) : [];
  const storageData = metrics?.storage ? [
    { name: 'Hot (PostgreSQL)', count: metrics.storage.hot.count, tier: 'hot' },
    { name: 'Warm (Compressed)', count: metrics.storage.warm.count, tier: 'warm', bytes: metrics.storage.warm.bytes },
    { name: 'Cold (Archived)', count: metrics.storage.cold.count, tier: 'cold', bytes: metrics.storage.cold.bytes },
  ] : [];

  const handleRefresh = () => {
    setLoading(true);
    Promise.all([fetchLogs(), fetchParsers(), fetchMetrics()])
      .finally(() => setLoading(false));
  };

  const handleCreateParser = async (values) => {
    try {
      await axios.post(`${API_BASE}/api/parsers`, values);
      notification.success({ message: 'Parser created successfully' });
      setParserModalVisible(false);
      fetchParsers();
    } catch (error) {
      notification.error({ message: 'Failed to create parser' });
    }
  };

  return (
    <Layout style={{ minHeight: '100vh', background: '#0a0e27' }}>
      <Header style={{ background: '#141b38', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <DatabaseOutlined style={{ fontSize: '24px', color: '#52c41a' }} />
          <h1 style={{ color: '#fff', margin: 0, fontSize: '20px' }}>Log Aggregation System</h1>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <span style={{ color: '#8c8c8c' }}>Auto Refresh</span>
          <Switch checked={autoRefresh} onChange={setAutoRefresh} />
          <Button icon={<ReloadOutlined />} onClick={handleRefresh} loading={loading}>
            Refresh
          </Button>
        </div>
      </Header>

      <Content style={{ padding: '24px', background: '#0a0e27' }}>
        {/* Metrics Cards */}
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col span={6}>
            <Card style={{ background: '#141b38', border: '1px solid #1f2937' }}>
              <Statistic
                title={<span style={{ color: '#8c8c8c' }}>Total Logs</span>}
                value={metrics?.total_logs || 0}
                valueStyle={{ color: '#52c41a' }}
                prefix={<DatabaseOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card style={{ background: '#141b38', border: '1px solid #1f2937' }}>
              <Statistic
                title={<span style={{ color: '#8c8c8c' }}>Hot Storage</span>}
                value={metrics?.storage?.hot?.count || 0}
                valueStyle={{ color: '#1890ff' }}
                prefix={<DatabaseOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card style={{ background: '#141b38', border: '1px solid #1f2937' }}>
              <Statistic
                title={<span style={{ color: '#8c8c8c' }}>Warm Storage</span>}
                value={metrics?.storage?.warm?.bytes ? (metrics.storage.warm.bytes / 1024 / 1024).toFixed(2) : 0}
                suffix="MB"
                valueStyle={{ color: '#faad14' }}
                prefix={<CloudUploadOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card style={{ background: '#141b38', border: '1px solid #1f2937' }}>
              <Statistic
                title={<span style={{ color: '#8c8c8c' }}>Active Parsers</span>}
                value={parsers.filter(p => p.enabled).length}
                valueStyle={{ color: '#722ed1' }}
                prefix={<SettingOutlined />}
              />
            </Card>
          </Col>
        </Row>

        {/* Charts */}
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col span={8}>
            <Card title={<span style={{ color: '#fff' }}>Logs by Level</span>} style={{ background: '#141b38', border: '1px solid #1f2937' }}>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={levelData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                    {levelData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#141b38', border: '1px solid #1f2937' }} />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </Col>
          <Col span={8}>
            <Card title={<span style={{ color: '#fff' }}>Logs by Service</span>} style={{ background: '#141b38', border: '1px solid #1f2937' }}>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={serviceData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                  <XAxis dataKey="name" stroke="#8c8c8c" />
                  <YAxis stroke="#8c8c8c" />
                  <Tooltip contentStyle={{ background: '#141b38', border: '1px solid #1f2937' }} />
                  <Bar dataKey="value" fill="#52c41a" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </Col>
          <Col span={8}>
            <Card title={<span style={{ color: '#fff' }}>Storage Distribution</span>} style={{ background: '#141b38', border: '1px solid #1f2937' }}>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={storageData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                  <XAxis dataKey="name" stroke="#8c8c8c" angle={-15} textAnchor="end" height={80} />
                  <YAxis stroke="#8c8c8c" />
                  <Tooltip contentStyle={{ background: '#141b38', border: '1px solid #1f2937' }} />
                  <Bar dataKey="count" fill="#1890ff" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </Col>
        </Row>

        {/* Filters and Controls */}
        <Card style={{ background: '#141b38', border: '1px solid #1f2937', marginBottom: '16px' }}>
          <Row gutter={16}>
            <Col span={6}>
              <Select
                style={{ width: '100%' }}
                placeholder="Filter by Service"
                allowClear
                onChange={(value) => setFilters({ ...filters, service: value })}
              >
                {serviceData.map(s => <Option key={s.name} value={s.name}>{s.name}</Option>)}
              </Select>
            </Col>
            <Col span={6}>
              <Select
                style={{ width: '100%' }}
                placeholder="Filter by Level"
                allowClear
                onChange={(value) => setFilters({ ...filters, level: value })}
              >
                <Option value="ERROR">ERROR</Option>
                <Option value="WARN">WARN</Option>
                <Option value="INFO">INFO</Option>
                <Option value="DEBUG">DEBUG</Option>
              </Select>
            </Col>
            <Col span={12} style={{ textAlign: 'right' }}>
              <Button icon={<SettingOutlined />} onClick={() => setParserModalVisible(true)} style={{ marginRight: '8px' }}>
                Manage Parsers
              </Button>
              <Button type="primary" icon={<SearchOutlined />} onClick={fetchLogs}>
                Search
              </Button>
            </Col>
          </Row>
        </Card>

        {/* Logs Table */}
        <Card title={<span style={{ color: '#fff' }}>Recent Logs</span>} style={{ background: '#141b38', border: '1px solid #1f2937' }}>
          <Table
            columns={columns}
            dataSource={logs}
            rowKey="id"
            pagination={{ pageSize: 20 }}
            size="small"
            style={{ background: '#0a0e27' }}
          />
        </Card>

        {/* Parser Modal */}
        <Modal
          title="Parsing Rules"
          open={parserModalVisible}
          onCancel={() => setParserModalVisible(false)}
          footer={null}
          width={800}
        >
          <Table
            columns={parserColumns}
            dataSource={parsers}
            rowKey="id"
            pagination={false}
            size="small"
          />
        </Modal>
      </Content>
    </Layout>
  );
}

export default App;
