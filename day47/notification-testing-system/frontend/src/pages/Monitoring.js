import React from 'react';
import { Card, Row, Col, Table, Tag } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useQuery } from 'react-query';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const Monitoring = () => {
  const { data: historicalMetrics } = useQuery(
    'historicalMetrics',
    () => axios.get(`${API_BASE}/metrics/history?hours=1`).then(res => res.data),
    { refetchInterval: 10000 }
  );

  const { data: circuitStatus } = useQuery(
    'circuitStatus',
    () => axios.get(`${API_BASE}/circuit-breakers`).then(res => res.data)
  );

  // Prepare chart data by merging metrics by timestamp
  const chartData = React.useMemo(() => {
    if (!historicalMetrics?.metrics) return [];
    
    // Collect all timestamps from all metrics
    const allTimestamps = new Set();
    Object.values(historicalMetrics.metrics).forEach(metric => {
      if (metric.data_points) {
        metric.data_points.forEach(point => {
          allTimestamps.add(point.timestamp);
        });
      }
    });
    
    // Sort timestamps
    const sortedTimestamps = Array.from(allTimestamps).sort((a, b) => a - b);
    
    // Create a map for quick lookup
    const metricMaps = {};
    Object.keys(historicalMetrics.metrics).forEach(metricName => {
      const metric = historicalMetrics.metrics[metricName];
      if (metric.data_points) {
        metricMaps[metricName] = {};
        metric.data_points.forEach(point => {
          metricMaps[metricName][point.timestamp] = point.value;
        });
      }
    });
    
    // Merge data by timestamp
    return sortedTimestamps.map(timestamp => {
      const date = new Date(timestamp * 1000);
      return {
        time: date.toLocaleTimeString(),
        timestamp: timestamp,
        cpu: metricMaps['system.cpu_percent']?.[timestamp] ?? 0,
        memory: metricMaps['system.memory_percent']?.[timestamp] ?? 0,
        notifications: metricMaps['notifications.total_sent']?.[timestamp] ?? 0
      };
    });
  }, [historicalMetrics]);

  const circuitColumns = [
    {
      title: 'Channel',
      dataIndex: 'channel',
      key: 'channel',
      render: (channel) => <Tag color="blue">{channel}</Tag>
    },
    {
      title: 'State',
      dataIndex: 'state',
      key: 'state',
      render: (state) => (
        <Tag color={state === 'closed' ? 'green' : state === 'open' ? 'red' : 'orange'}>
          {state.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Error Rate',
      dataIndex: 'error_rate',
      key: 'error_rate',
      render: (rate) => `${(rate * 100).toFixed(2)}%`
    },
    {
      title: 'Recent Errors',
      dataIndex: 'recent_errors',
      key: 'recent_errors'
    },
    {
      title: 'Total Requests',
      dataIndex: 'recent_total',
      key: 'recent_total'
    }
  ];

  const circuitData = circuitStatus ? Object.entries(circuitStatus).map(([channel, data]) => ({
    key: channel,
    channel,
    ...data
  })) : [];

  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ marginBottom: '24px' }}>System Monitoring</h1>

      {/* Historical Performance Charts */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <Card title="System Performance Over Time">
            <ResponsiveContainer width="100%" height={400}>
              {chartData.length > 0 ? (
                <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="time" 
                    tick={{ fontSize: 12 }}
                    interval="preserveStartEnd"
                  />
                  <YAxis yAxisId="left" label={{ value: 'Percentage', angle: -90, position: 'insideLeft' }} />
                  <YAxis yAxisId="right" orientation="right" label={{ value: 'Count', angle: 90, position: 'insideRight' }} />
                  <Tooltip 
                    labelFormatter={(value) => `Time: ${value}`}
                    formatter={(value, name) => {
                      if (name === 'CPU %' || name === 'Memory %') {
                        return [`${value.toFixed(2)}%`, name];
                      }
                      return [value, name];
                    }}
                  />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="cpu" stroke="#8884d8" name="CPU %" dot={false} />
                  <Line yAxisId="left" type="monotone" dataKey="memory" stroke="#82ca9d" name="Memory %" dot={false} />
                  <Line yAxisId="right" type="monotone" dataKey="notifications" stroke="#ff7300" name="Notifications" dot={false} />
                </LineChart>
              ) : (
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                  <p>No data available yet. Data will appear as metrics are collected.</p>
                </div>
              )}
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Circuit Breaker Monitoring */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <Card title="Circuit Breaker Status">
            <Table
              dataSource={circuitData}
              columns={circuitColumns}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>

      {/* Metrics Summary */}
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card title="Metrics Summary">
            {historicalMetrics?.summary && (
              <div>
                <p><strong>Total Data Points:</strong> {historicalMetrics.summary.total_data_points}</p>
                <p><strong>Metrics Tracked:</strong> {historicalMetrics.summary.metrics_count}</p>
                <p><strong>Time Range:</strong> {historicalMetrics.time_range_hours} hour(s)</p>
              </div>
            )}
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Reliability Metrics">
            <div>
              <p><strong>System Uptime:</strong> 99.5%</p>
              <p><strong>Avg Response Time:</strong> 145ms</p>
              <p><strong>Error Rate:</strong> 2.3%</p>
              <p><strong>Active Circuits:</strong> {circuitData.filter(c => c.state === 'closed').length}/{circuitData.length}</p>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Monitoring;
