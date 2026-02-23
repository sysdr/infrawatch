import React, { useState, useEffect, useCallback } from 'react';
import { Layout, Typography, Button, Space, Badge, Tooltip, notification, Spin, Row, Col } from 'antd';
import {
  DatabaseOutlined, ThunderboltOutlined, ReloadOutlined,
  CheckCircleOutlined, WarningOutlined, CloseCircleOutlined
} from '@ant-design/icons';
import axios from 'axios';
import SlowQueryPanel from './components/SlowQueryPanel';
import IndexHealthPanel from './components/IndexHealthPanel';
import PartitionPanel from './components/PartitionPanel';
import ReplicationPanel from './components/ReplicationPanel';
import SummaryCards from './components/SummaryCards';
import './App.css';

const { Header, Content } = Layout;
const { Title } = Typography;
const API = process.env.REACT_APP_API_URL || '';

export default function App() {
  const [summary, setSummary] = useState(null);
  const [slowQueries, setSlowQueries] = useState([]);
  const [indexHealth, setIndexHealth] = useState([]);
  const [partitions, setPartitions] = useState([]);
  const [replication, setReplication] = useState(null);
  const [connections, setConnections] = useState(null);
  const [bloat, setBloat] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [notifApi, contextHolder] = notification.useNotification();

  const fetchAll = useCallback(async () => {
    try {
      const [sumR, sqR, idxR, partR, replR, connR, bloatR] = await Promise.all([
        axios.get(`${API}/api/dashboard/summary`),
        axios.get(`${API}/api/queries/slow?limit=20`),
        axios.get(`${API}/api/indexes/health`),
        axios.get(`${API}/api/partitions/stats`),
        axios.get(`${API}/api/replication/status`),
        axios.get(`${API}/api/replication/connections`),
        axios.get(`${API}/api/maintenance/bloat`),
      ]);
      setSummary(sumR.data);
      setSlowQueries(sqR.data);
      setIndexHealth(idxR.data);
      setPartitions(partR.data);
      setReplication(replR.data);
      setConnections(connR.data);
      setBloat(bloatR.data);
      setLastRefresh(new Date().toLocaleTimeString());
    } catch (e) {
      notifApi.error({ message: 'Fetch error', description: e.message, duration: 3 });
    } finally {
      setLoading(false);
    }
  }, [notifApi]);

  useEffect(() => {
    fetchAll();
    const iv = setInterval(fetchAll, 5000);
    return () => clearInterval(iv);
  }, [fetchAll]);

  const handleVacuum = async (table) => {
    try {
      await axios.post(`${API}/api/maintenance/vacuum`, { table_name: table, analyze: true });
      notifApi.success({ message: `VACUUM ANALYZE completed on ${table}`, duration: 3 });
      fetchAll();
    } catch (e) {
      notifApi.error({ message: 'VACUUM failed', description: e.message });
    }
  };

  const handleAnalyze = async () => {
    try {
      await axios.post(`${API}/api/maintenance/analyze`);
      notifApi.success({ message: 'ANALYZE completed — statistics refreshed', duration: 3 });
      fetchAll();
    } catch (e) {
      notifApi.error({ message: 'ANALYZE failed', description: e.message });
    }
  };

  const overallHealth = summary
    ? summary.avg_query_latency_ms < 50 ? 'good'
      : summary.avg_query_latency_ms < 200 ? 'warn' : 'bad'
    : 'unknown';

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {contextHolder}
      <Header style={{
        background: '#1b4332', padding: '0 24px', display: 'flex',
        alignItems: 'center', justifyContent: 'space-between',
        height: '56px', boxShadow: '0 2px 8px rgba(0,0,0,0.3)'
      }}>
        <Space size={12}>
          <DatabaseOutlined style={{ color: '#52b788', fontSize: 22 }} />
          <Title level={4} style={{ color: 'white', margin: 0, fontWeight: 700 }}>
            DB Optimization
          </Title>
          <span style={{ color: '#74c69d', fontSize: 12 }}>Day 115 · Week 11 of 180</span>
        </Space>
        <Space size={12}>
          {lastRefresh && (
            <span style={{ color: '#74c69d', fontSize: 12 }}>Last: {lastRefresh}</span>
          )}
          <Badge
            color={overallHealth === 'good' ? '#52b788' : overallHealth === 'warn' ? '#fca311' : '#e63946'}
            text={<span style={{ color: 'white', fontSize: 12 }}>
              {overallHealth === 'good' ? 'Healthy' : overallHealth === 'warn' ? 'Degraded' : 'Critical'}
            </span>}
          />
          <Tooltip title="Refresh statistics"><Button
            icon={<ReloadOutlined />} onClick={fetchAll} size="small"
            style={{ background: '#2d6a4f', borderColor: '#52b788', color: 'white' }}
          /></Tooltip>
          <Button
            icon={<ThunderboltOutlined />} onClick={handleAnalyze} size="small"
            style={{ background: '#40916c', borderColor: '#52b788', color: 'white' }}
          >ANALYZE</Button>
        </Space>
      </Header>
      <Content style={{ padding: '20px 24px' }}>
        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
            <Spin size="large" tip="Connecting to database..." />
          </div>
        ) : (
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <SummaryCards summary={summary} connections={connections} />
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={14}>
                <SlowQueryPanel queries={slowQueries} />
              </Col>
              <Col xs={24} lg={10}>
                <IndexHealthPanel indexes={indexHealth} onRefresh={fetchAll} />
              </Col>
            </Row>
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={14}>
                <PartitionPanel partitions={partitions} />
              </Col>
              <Col xs={24} lg={10}>
                <ReplicationPanel
                  replication={replication}
                  connections={connections}
                  bloat={bloat}
                  onVacuum={handleVacuum}
                />
              </Col>
            </Row>
          </Space>
        )}
      </Content>
    </Layout>
  );
}
