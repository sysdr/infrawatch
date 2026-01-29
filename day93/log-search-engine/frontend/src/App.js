import React, { useState, useEffect, useCallback } from 'react';
import { Layout, Input, Button, Table, Card, Tag, Space, Select, Statistic, Row, Col, Tabs, message } from 'antd';
import { SearchOutlined, ReloadOutlined, BarChartOutlined, ThunderboltOutlined } from '@ant-design/icons';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import dayjs from 'dayjs';
import './App.css';

const { Header, Content } = Layout;
const { TextArea } = Input;

const API_BASE_URL = 'http://localhost:8000/api/v1';

const App = () => {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 50, total: 0 });
  const [facets, setFacets] = useState({ services: [], levels: [], timeline: [] });
  const [suggestions, setSuggestions] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [realTimeEnabled, setRealTimeEnabled] = useState(false);

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
      width: 100,
      render: (level) => {
        const colors = {
          error: 'red',
          warning: 'orange',
          info: 'blue',
          critical: 'purple',
          debug: 'green'
        };
        return <Tag color={colors[level] || 'default'}>{(level || '').toUpperCase()}</Tag>;
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
      title: 'Request ID',
      dataIndex: 'request_id',
      key: 'request_id',
      width: 150,
      ellipsis: true,
    },
  ];

  const handleSearch = useCallback(async (page = 1) => {
    if (!query.trim()) {
      message.warning('Please enter a search query');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/search`, {
        params: {
          q: query,
          page: page,
          page_size: pagination.pageSize,
        },
      });

      setSearchResults(response.data.logs);
      setPagination({
        ...pagination,
        current: page,
        total: response.data.total,
      });

      // Fetch facets
      const facetResponse = await axios.get(`${API_BASE_URL}/facets`, {
        params: { q: query },
      });
      setFacets(facetResponse.data);

    } catch (error) {
      message.error('Search failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  }, [query, pagination.pageSize]);

  const handleQueryChange = async (value) => {
    setQuery(value);
    
    if (value.length > 2) {
      try {
        const response = await axios.get(`${API_BASE_URL}/suggestions`, {
          params: { q: value },
        });
        setSuggestions(response.data.suggestions);
      } catch (error) {
        console.error('Failed to fetch suggestions:', error);
      }
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/analytics`);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    }
  };

  const handleTableChange = (newPagination) => {
    handleSearch(newPagination.current);
  };

  const handleFacetClick = (field, value) => {
    const newQuery = query ? `${query} AND ${field}:${value}` : `${field}:${value}`;
    setQuery(newQuery);
  };

  useEffect(() => {
    loadAnalytics();
  }, []);

  const exampleQueries = [
    'level:error',
    'service:api',
    'level:error AND service:api',
    'message:*timeout*',
    'level:error OR level:critical',
    'timestamp:[2025-01-01 TO 2025-01-31]'
  ];

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Header style={{ background: '#1890ff', padding: '0 24px', display: 'flex', alignItems: 'center' }}>
        <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
          <ThunderboltOutlined /> Log Search Engine
        </div>
      </Header>

      <Content style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', width: '100%' }}>
        <Card
          title={
            <Space>
              <SearchOutlined />
              <span>Search Logs</span>
            </Space>
          }
          extra={
            <Button 
              icon={<ReloadOutlined />} 
              onClick={() => handleSearch(1)}
              loading={loading}
            >
              Refresh
            </Button>
          }
          style={{ marginBottom: '24px' }}
        >
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <div>
              <TextArea
                placeholder="Enter search query (e.g., level:error AND service:api)"
                value={query}
                onChange={(e) => handleQueryChange(e.target.value)}
                onPressEnter={() => handleSearch(1)}
                autoSize={{ minRows: 2, maxRows: 4 }}
                style={{ fontSize: '14px' }}
              />
              {suggestions.length > 0 && (
                <div style={{ marginTop: '8px' }}>
                  <Space wrap>
                    {suggestions.map((suggestion, idx) => (
                      <Tag
                        key={idx}
                        style={{ cursor: 'pointer' }}
                        onClick={() => setQuery(suggestion)}
                      >
                        {suggestion}
                      </Tag>
                    ))}
                  </Space>
                </div>
              )}
            </div>

            <div>
              <div style={{ marginBottom: '12px', color: '#666' }}>Quick Examples:</div>
              <Space wrap>
                {exampleQueries.map((exampleQuery, idx) => (
                  <Tag
                    key={idx}
                    color="blue"
                    style={{ cursor: 'pointer' }}
                    onClick={() => {
                      setQuery(exampleQuery);
                      handleSearch(1);
                    }}
                  >
                    {exampleQuery}
                  </Tag>
                ))}
              </Space>
            </div>

            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={() => handleSearch(1)}
              loading={loading}
              size="large"
            >
              Search
            </Button>
          </Space>
        </Card>

        <Tabs
          defaultActiveKey="results"
          items={[
            {
              key: 'results',
              label: 'Search Results',
              children: (
                <>
                  <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                    <Col span={8}>
                      <Card>
                        <Statistic
                          title="Total Results"
                          value={pagination.total}
                          prefix={<SearchOutlined />}
                        />
                      </Card>
                    </Col>
                    <Col span={8}>
                      <Card>
                        <Statistic
                          title="Current Page"
                          value={`${pagination.current} / ${Math.ceil(pagination.total / pagination.pageSize)}`}
                        />
                      </Card>
                    </Col>
                    <Col span={8}>
                      <Card>
                        <Statistic
                          title="Results per Page"
                          value={pagination.pageSize}
                        />
                      </Card>
                    </Col>
                  </Row>

                  <Table
                    columns={columns}
                    dataSource={searchResults}
                    loading={loading}
                    pagination={pagination}
                    onChange={handleTableChange}
                    rowKey="id"
                    scroll={{ x: 1000 }}
                  />
                </>
              ),
            },
            {
              key: 'facets',
              label: 'Facets',
              children: (
                <Row gutter={[16, 16]}>
                  <Col span={8}>
                    <Card title="Services">
                      <Space direction="vertical" style={{ width: '100%' }}>
                        {facets.services.map((facet, idx) => (
                          <div
                            key={idx}
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              padding: '8px',
                              cursor: 'pointer',
                              borderRadius: '4px',
                              background: idx % 2 === 0 ? '#fafafa' : 'white',
                            }}
                            onClick={() => handleFacetClick('service', facet.value)}
                          >
                            <span>{facet.value}</span>
                            <Tag color="blue">{facet.count}</Tag>
                          </div>
                        ))}
                      </Space>
                    </Card>
                  </Col>

                  <Col span={8}>
                    <Card title="Log Levels">
                      <Space direction="vertical" style={{ width: '100%' }}>
                        {facets.levels.map((facet, idx) => (
                          <div
                            key={idx}
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              padding: '8px',
                              cursor: 'pointer',
                              borderRadius: '4px',
                              background: idx % 2 === 0 ? '#fafafa' : 'white',
                            }}
                            onClick={() => handleFacetClick('level', facet.value)}
                          >
                            <span>{facet.value}</span>
                            <Tag color="orange">{facet.count}</Tag>
                          </div>
                        ))}
                      </Space>
                    </Card>
                  </Col>

                  <Col span={8}>
                    <Card title="Timeline (24h)">
                      <ResponsiveContainer width="100%" height={200}>
                        <LineChart data={facets.timeline}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis
                            dataKey="time"
                            tickFormatter={(time) => dayjs(time).format('HH:mm')}
                          />
                          <YAxis />
                          <Tooltip
                            labelFormatter={(time) => dayjs(time).format('YYYY-MM-DD HH:mm')}
                          />
                          <Line type="monotone" dataKey="count" stroke="#1890ff" />
                        </LineChart>
                      </ResponsiveContainer>
                    </Card>
                  </Col>
                </Row>
              ),
            },
            {
              key: 'analytics',
              label: <span><BarChartOutlined /> Analytics</span>,
              children: (
                <>
                  {analytics ? (
                    <>
                      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                        <Col span={8}>
                          <Card>
                            <Statistic
                              title="Average Query Time"
                              value={Number(analytics.avg_execution_time_ms ?? 0).toFixed(2)}
                              suffix="ms"
                            />
                          </Card>
                        </Col>
                        <Col span={8}>
                          <Card>
                            <Statistic
                              title="Cache Hit Rate"
                              value={(Number(analytics.cache_hit_rate ?? 0) * 100).toFixed(1)}
                              suffix="%"
                            />
                          </Card>
                        </Col>
                        <Col span={8}>
                          <Card>
                            <Statistic
                              title="Total Queries"
                              value={analytics.total_queries ?? 0}
                            />
                          </Card>
                        </Col>
                      </Row>
                      <Card title="Most Common Queries">
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart data={analytics.common_queries ?? []}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="query" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="count" fill="#52c41a" />
                          </BarChart>
                        </ResponsiveContainer>
                      </Card>
                    </>
                  ) : (
                    <Card><Statistic title="Analytics" value="Loading..." /></Card>
                  )}
                </>
              ),
            },
          ]}
        />
      </Content>
    </Layout>
  );
};

export default App;
