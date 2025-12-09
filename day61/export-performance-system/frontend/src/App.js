import React, { useState, useEffect } from 'react';
import { Layout, Card, Row, Col, Statistic, Button, Table, Tag, message, Space, Select, DatePicker } from 'antd';
import { ThunderboltOutlined, DatabaseOutlined, ClockCircleOutlined, CloudDownloadOutlined, ReloadOutlined } from '@ant-design/icons';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import './App.css';

const { Header, Content } = Layout;
const { RangePicker } = DatePicker;

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [metrics, setMetrics] = useState(null);
  const [cacheStats, setCacheStats] = useState(null);
  const [slowQueries, setSlowQueries] = useState([]);
  const [slowQueriesNote, setSlowQueriesNote] = useState(null);
  const [poolStatus, setPoolStatus] = useState(null);
  const [indexStatus, setIndexStatus] = useState([]);
  const [performanceHistory, setPerformanceHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [exportParams, setExportParams] = useState({
    userId: '',
    format: 'json'
  });

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchAllData = async () => {
    try {
      const [metricsRes, cacheRes, slowRes, poolRes, indexRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/performance/metrics`),
        axios.get(`${API_BASE_URL}/api/cache/stats`),
        axios.get(`${API_BASE_URL}/api/performance/slow-queries`),
        axios.get(`${API_BASE_URL}/api/resources/pool-status`),
        axios.get(`${API_BASE_URL}/api/indexes/status`)
      ]);

      setMetrics(metricsRes.data);
      setCacheStats(cacheRes.data);
      setSlowQueries(slowRes.data.queries || []);
      setSlowQueriesNote(slowRes.data.note || null);
      setPoolStatus(poolRes.data);
      setIndexStatus(indexRes.data.indexes || []);

      // Update performance history
      setPerformanceHistory(prev => {
        const newPoint = {
          time: new Date().toLocaleTimeString(),
          p50: metricsRes.data.query_times.p50_ms,
          p95: metricsRes.data.query_times.p95_ms,
          p99: metricsRes.data.query_times.p99_ms
        };
        return [...prev.slice(-20), newPoint];
      });
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const handleExport = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/exports/notifications`, exportParams);
      message.success(`Export completed in ${response.data.execution_time_ms}ms (${response.data.source})`);
      fetchAllData();
    } catch (error) {
      message.error('Export failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCacheInvalidate = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/cache/invalidate`, null, { params: { pattern: '*' } });
      message.success('Cache invalidated successfully');
      fetchAllData();
    } catch (error) {
      message.error('Cache invalidation failed');
    }
  };

  const slowQueryColumns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (text) => new Date(text).toLocaleString()
    },
    {
      title: 'Query Time',
      dataIndex: 'query_time_ms',
      key: 'query_time_ms',
      render: (time, record) => {
        if (record.cached) {
          return <Tag color="green">Cached ({record.total_time_ms || 0}ms)</Tag>;
        }
        const color = time > 1000 ? 'red' : time > 500 ? 'orange' : 'green';
        return <Tag color={color}>{time}ms</Tag>;
      }
    },
    {
      title: 'Rows',
      dataIndex: 'row_count',
      key: 'row_count'
    },
    {
      title: 'Source',
      dataIndex: 'cached',
      key: 'cached',
      render: (cached) => <Tag color={cached ? 'green' : 'blue'}>{cached ? 'Cache' : 'Database'}</Tag>
    }
  ];

  const indexColumns = [
    {
      title: 'Table',
      dataIndex: 'table',
      key: 'table'
    },
    {
      title: 'Index Name',
      dataIndex: 'index',
      key: 'index'
    },
    {
      title: 'Scans',
      dataIndex: 'scans',
      key: 'scans',
      render: (scans) => scans?.toLocaleString() || '0'
    },
    {
      title: 'Tuples Read',
      dataIndex: 'tuples_read',
      key: 'tuples_read',
      render: (tuples) => tuples?.toLocaleString() || '0'
    }
  ];

  if (!metrics || !cacheStats) {
    return <div style={{ padding: '50px', textAlign: 'center' }}>Loading dashboard...</div>;
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#001529', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
          <ThunderboltOutlined /> Export Performance Dashboard
        </div>
        <Button icon={<ReloadOutlined />} onClick={fetchAllData}>Refresh</Button>
      </Header>
      <Content style={{ padding: '24px', background: '#f0f2f5' }}>
        {/* Key Metrics */}
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Average Query Time"
                value={metrics.query_times.avg_ms}
                suffix="ms"
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: metrics.query_times.avg_ms < 100 ? '#3f8600' : '#cf1322' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Cache Hit Rate"
                value={cacheStats.hit_rate_percent}
                suffix="%"
                prefix={<DatabaseOutlined />}
                valueStyle={{ color: cacheStats.hit_rate_percent > 70 ? '#3f8600' : '#cf1322' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Total Exports"
                value={metrics.exports.total}
                prefix={<CloudDownloadOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Pool Utilization"
                value={poolStatus?.utilization_percent || 0}
                suffix="%"
                valueStyle={{ color: (poolStatus?.utilization_percent || 0) < 70 ? '#3f8600' : '#cf1322' }}
              />
            </Card>
          </Col>
        </Row>

        {/* Export Controls */}
        <Card title="Export Data" style={{ marginTop: 16 }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Space wrap>
              <Select
                style={{ width: 200 }}
                placeholder="Select User"
                value={exportParams.userId || undefined}
                onChange={(value) => setExportParams({...exportParams, userId: value})}
                allowClear
              >
                {[...Array(10)].map((_, i) => (
                  <Select.Option key={i} value={`user${i}`}>user{i}</Select.Option>
                ))}
              </Select>
              <Select
                style={{ width: 150 }}
                value={exportParams.format}
                onChange={(value) => setExportParams({...exportParams, format: value})}
              >
                <Select.Option value="json">JSON</Select.Option>
                <Select.Option value="csv">CSV</Select.Option>
                <Select.Option value="xlsx">Excel</Select.Option>
              </Select>
              <Button type="primary" onClick={handleExport} loading={loading} icon={<CloudDownloadOutlined />}>
                Export Data
              </Button>
              <Button onClick={handleCacheInvalidate}>Invalidate Cache</Button>
            </Space>
          </Space>
        </Card>

        {/* Performance Charts */}
        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} lg={12}>
            <Card title="Query Performance Percentiles">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceHistory}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis label={{ value: 'Time (ms)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="p50" stroke="#52c41a" name="P50" />
                  <Line type="monotone" dataKey="p95" stroke="#faad14" name="P95" />
                  <Line type="monotone" dataKey="p99" stroke="#f5222d" name="P99" />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="System Resources">
              <Row gutter={16}>
                <Col span={12}>
                  <Statistic
                    title="CPU Usage"
                    value={metrics.system.cpu_percent}
                    suffix="%"
                    valueStyle={{ color: metrics.system.cpu_percent < 70 ? '#3f8600' : '#cf1322' }}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="Memory Usage"
                    value={metrics.system.memory_percent}
                    suffix="%"
                    valueStyle={{ color: metrics.system.memory_percent < 80 ? '#3f8600' : '#cf1322' }}
                  />
                </Col>
                <Col span={24} style={{ marginTop: 16 }}>
                  <Statistic
                    title="DB Pool"
                    value={`${poolStatus?.checked_out || 0} / ${poolStatus?.total_connections || 0}`}
                    prefix="Active:"
                  />
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>

        {/* Cache Statistics */}
        <Card title="Cache Performance" style={{ marginTop: 16 }}>
          <Row gutter={16}>
            <Col span={6}>
              <Statistic title="Total Hits" value={cacheStats.total_hits} />
            </Col>
            <Col span={6}>
              <Statistic title="Total Misses" value={cacheStats.total_misses} />
            </Col>
            <Col span={6}>
              <Statistic title="Memory Cache" value={cacheStats.memory_hits} />
            </Col>
            <Col span={6}>
              <Statistic title="Redis Cache" value={cacheStats.redis_hits} />
            </Col>
          </Row>
        </Card>

        {/* Slow Queries */}
        <Card 
          title="Slow Query Log (>500ms)" 
          style={{ marginTop: 16 }}
          extra={slowQueriesNote && <span style={{ color: '#8c8c8c', fontSize: '12px' }}>{slowQueriesNote}</span>}
        >
          {slowQueries.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '20px', color: '#8c8c8c' }}>
              No queries yet. Run an export to see query performance data.
            </div>
          ) : (
            <Table
              columns={slowQueryColumns}
              dataSource={slowQueries}
              rowKey={(record, index) => `${record.timestamp}-${index}`}
              pagination={{ pageSize: 10 }}
              size="small"
            />
          )}
        </Card>

        {/* Index Status */}
        <Card title="Database Indexes" style={{ marginTop: 16 }}>
          <Table
            columns={indexColumns}
            dataSource={indexStatus}
            rowKey={(record) => record.index}
            pagination={false}
            size="small"
          />
        </Card>
      </Content>
    </Layout>
  );
}

export default App;
