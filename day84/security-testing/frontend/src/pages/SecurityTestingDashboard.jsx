import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Button, Table, Tag, Progress, Tabs, Modal, Timeline } from 'antd';
import { 
  SafetyOutlined, 
  ExperimentOutlined, 
  AlertOutlined, 
  CheckCircleOutlined,
  CloseCircleOutlined,
  RocketOutlined,
  FileSearchOutlined
} from '@ant-design/icons';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const SecurityTestingDashboard = () => {
  const [stats, setStats] = useState(null);
  const [events, setEvents] = useState([]);
  const [testResults, setTestResults] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [testRunning, setTestRunning] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, eventsRes, testsRes, incidentsRes] = await Promise.all([
        axios.get(`${API_BASE}/api/dashboard/stats`),
        axios.get(`${API_BASE}/api/events?limit=50`),
        axios.get(`${API_BASE}/api/tests/results`),
        axios.get(`${API_BASE}/api/incidents`)
      ]);
      
      setStats(statsRes.data);
      setEvents(eventsRes.data);
      setTestResults(testsRes.data);
      setIncidents(incidentsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const runUnitTests = async () => {
    setTestRunning(true);
    try {
      const response = await axios.post(`${API_BASE}/api/tests/unit/run`);
      Modal.success({
        title: 'Unit Tests Complete',
        content: `Passed: ${response.data.passed}/${response.data.total_tests} (${response.data.duration_ms}ms)`
      });
      fetchData();
    } catch (error) {
      Modal.error({ title: 'Test Failed', content: error.message });
    } finally {
      setTestRunning(false);
    }
  };

  const runIntegrationTests = async () => {
    setTestRunning(true);
    try {
      const response = await axios.post(`${API_BASE}/api/tests/integration/run`);
      Modal.success({
        title: 'Integration Tests Complete',
        content: `Passed: ${response.data.passed}/${response.data.total_tests} (${response.data.duration_ms}ms)`
      });
      fetchData();
    } catch (error) {
      Modal.error({ title: 'Test Failed', content: error.message });
    } finally {
      setTestRunning(false);
    }
  };

  const runChaosTests = async () => {
    setTestRunning(true);
    try {
      const response = await axios.post(`${API_BASE}/api/tests/chaos/run`);
      Modal.success({
        title: 'Chaos Tests Complete',
        content: `Scenarios: ${response.data.total_scenarios} (${response.data.duration_ms}ms)`
      });
      fetchData();
    } catch (error) {
      Modal.error({ title: 'Test Failed', content: error.message });
    } finally {
      setTestRunning(false);
    }
  };

  const runAssessment = async () => {
    setTestRunning(true);
    try {
      const response = await axios.post(`${API_BASE}/api/assessment/run`);
      Modal.success({
        title: 'Security Assessment Complete',
        content: `Score: ${response.data.score.toFixed(1)}% | Status: ${response.data.status}`
      });
      fetchData();
    } catch (error) {
      Modal.error({ title: 'Assessment Failed', content: error.message });
    } finally {
      setTestRunning(false);
    }
  };

  const eventColumns = [
    {
      title: 'Time',
      dataIndex: 'detected_at',
      key: 'detected_at',
      render: (time) => time ? new Date(time).toLocaleTimeString() : '-',
      width: 100
    },
    {
      title: 'Type',
      dataIndex: 'event_type',
      key: 'event_type',
      render: (type) => <Tag color="blue">{type}</Tag>
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      render: (severity) => (
        <Tag color={
          severity === 'critical' ? 'red' :
          severity === 'high' ? 'orange' :
          severity === 'medium' ? 'gold' : 'green'
        }>
          {severity ? severity.toUpperCase() : '-'}
        </Tag>
      )
    },
    {
      title: 'Source IP',
      dataIndex: 'source_ip',
      key: 'source_ip',
      width: 130
    },
    {
      title: 'Endpoint',
      dataIndex: 'endpoint',
      key: 'endpoint',
      ellipsis: true
    },
    {
      title: 'Threat Score',
      dataIndex: 'threat_score',
      key: 'threat_score',
      render: (score) => (
        <Progress 
          percent={Math.round((score || 0) * 100)} 
          size="small"
          strokeColor={score > 0.8 ? '#ff4d4f' : score > 0.5 ? '#faad14' : '#52c41a'}
        />
      ),
      width: 150
    },
    {
      title: 'Status',
      dataIndex: 'response_status',
      key: 'response_status',
      render: (status) => status ? <Tag>{status}</Tag> : '-'
    }
  ];

  const testColumns = [
    {
      title: 'Test Name',
      dataIndex: 'test_name',
      key: 'test_name',
      ellipsis: true
    },
    {
      title: 'Type',
      dataIndex: 'test_type',
      key: 'test_type',
      render: (type) => <Tag color="purple">{type}</Tag>
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        status === 'passed' ? 
          <Tag icon={<CheckCircleOutlined />} color="success">PASSED</Tag> :
          <Tag icon={<CloseCircleOutlined />} color="error">FAILED</Tag>
      )
    },
    {
      title: 'Duration',
      dataIndex: 'duration_ms',
      key: 'duration_ms',
      render: (ms) => ms ? `${ms}ms` : '-',
      width: 100
    },
    {
      title: 'Started At',
      dataIndex: 'started_at',
      key: 'started_at',
      render: (time) => time ? new Date(time).toLocaleString() : '-',
      width: 180
    }
  ];

  return (
    <div style={{ padding: '24px', background: '#f0f2f5', minHeight: '100vh' }}>
      <h1 style={{ marginBottom: '24px', fontSize: '28px', fontWeight: 600 }}>
        <SafetyOutlined style={{ marginRight: '12px' }} />
        Security Testing & Validation Platform
      </h1>

      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Security Events (24h)"
              value={stats?.total_events_24h || 0}
              prefix={<AlertOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Critical Events"
              value={stats?.critical_events_24h || 0}
              prefix={<AlertOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Active Incidents"
              value={stats?.active_incidents || 0}
              prefix={<SafetyOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Test Pass Rate"
              value={stats?.test_pass_rate || 0}
              suffix="%"
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
      </Row>

      <Card 
        title={<><ExperimentOutlined /> Test Execution Controls</>}
        style={{ marginBottom: '24px' }}
      >
        <Row gutter={16}>
          <Col span={6}>
            <Button 
              type="primary" 
              block 
              onClick={runUnitTests}
              loading={testRunning}
              icon={<CheckCircleOutlined />}
            >
              Run Unit Tests
            </Button>
          </Col>
          <Col span={6}>
            <Button 
              type="primary" 
              block 
              onClick={runIntegrationTests}
              loading={testRunning}
              icon={<CheckCircleOutlined />}
            >
              Run Integration Tests
            </Button>
          </Col>
          <Col span={6}>
            <Button 
              type="danger" 
              block 
              onClick={runChaosTests}
              loading={testRunning}
              icon={<RocketOutlined />}
            >
              Run Chaos Tests
            </Button>
          </Col>
          <Col span={6}>
            <Button 
              block 
              onClick={runAssessment}
              loading={testRunning}
              icon={<FileSearchOutlined />}
            >
              Run Security Assessment
            </Button>
          </Col>
        </Row>
      </Card>

      <Card>
        <Tabs 
          defaultActiveKey="events"
          items={[
            {
              key: 'events',
              label: 'Security Events',
              children: (
                <Table 
                  columns={eventColumns} 
                  dataSource={events}
                  rowKey="id"
                  pagination={{ pageSize: 20 }}
                  scroll={{ y: 400 }}
                />
              )
            },
            {
              key: 'tests',
              label: 'Test Results',
              children: (
                <Table 
                  columns={testColumns} 
                  dataSource={testResults}
                  rowKey="id"
                  pagination={{ pageSize: 20 }}
                  scroll={{ y: 400 }}
                />
              )
            },
            {
              key: 'incidents',
              label: 'Incidents',
              children: (
                <Timeline>
                  {incidents.map(incident => (
                    <Timeline.Item 
                      key={incident.id}
                      color={
                        incident.severity === 'critical' ? 'red' :
                        incident.severity === 'high' ? 'orange' : 'blue'
                      }
                    >
                      <p><strong>{incident.incident_id}</strong> - {incident.severity ? incident.severity.toUpperCase() : '-'}</p>
                      <p>Status: <Tag>{incident.status}</Tag> | Events: {incident.event_count}</p>
                      <p style={{ fontSize: '12px', color: '#666' }}>
                        {incident.first_detected ? new Date(incident.first_detected).toLocaleString() : '-'}
                      </p>
                    </Timeline.Item>
                  ))}
                </Timeline>
              )
            }
          ]}
        />
      </Card>
    </div>
  );
};

export default SecurityTestingDashboard;
