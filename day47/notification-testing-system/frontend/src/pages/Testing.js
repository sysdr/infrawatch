import React, { useState } from 'react';
import { Card, Button, Form, Select, Input, Row, Col, Alert, Progress, Table, Tag, Space } from 'antd';
import { PlayCircleOutlined, LoadingOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Option } = Select;
const { TextArea } = Input;

const API_BASE = 'http://localhost:8000/api';

const Testing = () => {
  const [testResults, setTestResults] = useState(null);
  const [isRunningTest, setIsRunningTest] = useState(false);
  const [performanceResults, setPerformanceResults] = useState(null);
  const [isRunningPerf, setIsRunningPerf] = useState(false);

  const runIntegrationTests = async () => {
    setIsRunningTest(true);
    try {
      const response = await axios.post(`${API_BASE}/testing/integration`);
      setTestResults(response.data);
    } catch (error) {
      console.error('Integration test failed:', error);
      setTestResults({ success: false, error: error.message });
    }
    setIsRunningTest(false);
  };

  const runPerformanceTest = async (values) => {
    setIsRunningPerf(true);
    try {
      const response = await axios.post(`${API_BASE}/testing/performance`, values);
      setPerformanceResults(response.data);
    } catch (error) {
      console.error('Performance test failed:', error);
      setPerformanceResults({ success: false, error: error.message });
    }
    setIsRunningPerf(false);
  };

  const sendTestNotification = async (values) => {
    try {
      const response = await axios.post(`${API_BASE}/notifications/test`, values);
      alert(response.data.success ? 'Test notification sent successfully!' : 'Test notification failed: ' + response.data.error);
    } catch (error) {
      alert('Test failed: ' + error.message);
    }
  };

  const testColumns = [
    {
      title: 'Test Name',
      dataIndex: 'test_name',
      key: 'test_name',
    },
    {
      title: 'Channel',
      dataIndex: 'channel',
      key: 'channel',
      render: (channel) => <Tag color="blue">{channel}</Tag>
    },
    {
      title: 'Status',
      dataIndex: 'success',
      key: 'success',
      render: (success) => (
        <Tag color={success ? 'green' : 'red'}>
          {success ? 'PASS' : 'FAIL'}
        </Tag>
      )
    },
    {
      title: 'Duration',
      dataIndex: 'duration_ms',
      key: 'duration_ms',
      render: (duration) => `${Math.round(duration)}ms`
    },
    {
      title: 'Details',
      dataIndex: 'error',
      key: 'details',
      render: (error, record) => error || (record.details ? JSON.stringify(record.details, null, 2) : 'Success')
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ marginBottom: '24px' }}>Notification Testing</h1>

      {/* Test Notification */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <Card title="Send Test Notification">
            <Form layout="vertical" onFinish={sendTestNotification}>
              <Row gutter={16}>
                <Col span={6}>
                  <Form.Item name="user_id" label="User ID" rules={[{ required: true }]}>
                    <Input placeholder="test_user_123" />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item name="channel" label="Channel" rules={[{ required: true }]}>
                    <Select placeholder="Select channel">
                      <Option value="email">Email</Option>
                      <Option value="sms">SMS</Option>
                      <Option value="push">Push</Option>
                      <Option value="webhook">Webhook</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item name="priority" label="Priority">
                    <Select defaultValue="normal">
                      <Option value="low">Low</Option>
                      <Option value="normal">Normal</Option>
                      <Option value="high">High</Option>
                      <Option value="urgent">Urgent</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item label=" ">
                    <Button type="primary" htmlType="submit" icon={<PlayCircleOutlined />}>
                      Send Test
                    </Button>
                  </Form.Item>
                </Col>
              </Row>
              <Row>
                <Col span={24}>
                  <Form.Item name="content" label="Message Content" rules={[{ required: true }]}>
                    <TextArea rows={3} placeholder="Enter your test notification content here..." />
                  </Form.Item>
                </Col>
              </Row>
            </Form>
          </Card>
        </Col>
      </Row>

      {/* Integration Testing */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={12}>
          <Card title="Integration Testing">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button 
                type="primary" 
                size="large" 
                onClick={runIntegrationTests}
                loading={isRunningTest}
                icon={isRunningTest ? <LoadingOutlined /> : <PlayCircleOutlined />}
                block
              >
                {isRunningTest ? 'Running Integration Tests...' : 'Run Integration Tests'}
              </Button>
              
              {testResults && (
                <div>
                  <Alert
                    message={testResults.success ? 'Integration Tests Completed' : 'Integration Tests Failed'}
                    description={testResults.success ? 
                      `${testResults.results?.summary?.passed_tests || 0} of ${testResults.results?.summary?.total_tests || 0} tests passed` :
                      testResults.error
                    }
                    type={testResults.success ? 'success' : 'error'}
                    style={{ marginTop: '16px' }}
                  />
                  
                  {testResults.success && testResults.results?.summary && (
                    <div style={{ marginTop: '16px' }}>
                      <h4>Test Summary</h4>
                      <Progress
                        percent={Math.round(testResults.results.summary.pass_rate * 100)}
                        status={testResults.results.summary.pass_rate === 1 ? 'success' : 'active'}
                      />
                      <p>Average Duration: {Math.round(testResults.results.summary.avg_duration_ms)}ms</p>
                    </div>
                  )}
                </div>
              )}
            </Space>
          </Card>
        </Col>
        
        <Col span={12}>
          <Card title="Performance Testing">
            <Form layout="vertical" onFinish={runPerformanceTest}>
              <Form.Item name="type" label="Test Type" initialValue="sustained">
                <Select>
                  <Option value="burst">Burst Load</Option>
                  <Option value="sustained">Sustained Load</Option>
                  <Option value="mixed">Mixed Workload</Option>
                  <Option value="ramp">Ramp Load</Option>
                </Select>
              </Form.Item>
              
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="target_rps" label="Target RPS" initialValue={10}>
                    <Input type="number" min={1} max={1000} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="duration_seconds" label="Duration (s)" initialValue={30}>
                    <Input type="number" min={10} max={300} />
                  </Form.Item>
                </Col>
              </Row>
              
              <Button 
                type="primary" 
                htmlType="submit"
                loading={isRunningPerf}
                icon={isRunningPerf ? <LoadingOutlined /> : <PlayCircleOutlined />}
                block
              >
                {isRunningPerf ? 'Running Performance Test...' : 'Run Performance Test'}
              </Button>
            </Form>
            
            {performanceResults && (
              <div style={{ marginTop: '16px' }}>
                <Alert
                  message={performanceResults.success ? 'Performance Test Completed' : 'Performance Test Failed'}
                  description={performanceResults.success ?
                    `${performanceResults.results?.summary?.total_requests || 0} requests, ${(performanceResults.results?.summary?.success_rate * 100 || 0).toFixed(1)}% success rate` :
                    performanceResults.error
                  }
                  type={performanceResults.success ? 'success' : 'error'}
                />
                
                {performanceResults.success && performanceResults.results?.summary && (
                  <div style={{ marginTop: '16px' }}>
                    <h4>Performance Summary</h4>
                    <p><strong>Throughput:</strong> {(performanceResults.results.summary.throughput_rps || 0).toFixed(1)} RPS</p>
                    <p><strong>Avg Latency:</strong> {Math.round(performanceResults.results.summary.avg_latency_ms || 0)}ms</p>
                    <p><strong>P95 Latency:</strong> {Math.round(performanceResults.results.summary.p95_latency_ms || 0)}ms</p>
                  </div>
                )}
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* Test Results Table */}
      {testResults?.success && testResults.results?.tests && (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card title="Detailed Test Results">
              <Table
                dataSource={testResults.results.tests}
                columns={testColumns}
                pagination={false}
                size="small"
                rowKey="test_name"
              />
            </Card>
          </Col>
        </Row>
      )}
    </div>
  );
};

export default Testing;
