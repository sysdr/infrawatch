import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Button, Modal, Descriptions } from 'antd';
import { HeartOutlined, EyeOutlined, ReloadOutlined } from '@ant-design/icons';

function HealthMonitoring() {
  const [servers, setServers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedServer, setSelectedServer] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);

  useEffect(() => {
    fetchServers();
    const interval = setInterval(fetchServers, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchServers = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/validation/health-dashboard');
      const data = await response.json();
      if (data.status === 'success' && data.dashboard) {
        setServers(data.dashboard.servers.map(server => ({
          ...server,
          ip_address: server.ip, // Map 'ip' to 'ip_address' for consistency
          last_check: data.dashboard.last_updated * 1000, // Convert to milliseconds
          id: server.hostname // Add an id field for React keys
        })) || []);
      }
    } catch (error) {
      console.error('Failed to fetch servers:', error);
    } finally {
      setLoading(false);
    }
  };

  const viewServerDetails = async (serverId) => {
    try {
      const response = await fetch(`/api/validation/server-health/${serverId}`);
      const data = await response.json();
      setSelectedServer(data);
      setModalVisible(true);
    } catch (error) {
      console.error('Failed to fetch server details:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'green';
      case 'degraded': return 'orange';
      case 'unhealthy': return 'red';
      case 'unreachable': return 'gray';
      default: return 'blue';
    }
  };

  const columns = [
    {
      title: 'Server',
      key: 'server',
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{record.hostname}</div>
          <div style={{ color: '#666', fontSize: '12px' }}>{record.ip_address}</div>
        </div>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={getStatusColor(status)}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Response Time',
      dataIndex: 'response_time',
      key: 'response_time',
      render: (time) => `${Math.round(time || 0)}ms`,
    },
    {
      title: 'Last Check',
      dataIndex: 'last_check',
      key: 'last_check',
      render: (time) => time ? new Date(time).toLocaleString() : 'Never',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Button 
          type="link" 
          icon={<EyeOutlined />}
          onClick={() => viewServerDetails(record.id)}
        >
          Details
        </Button>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1><HeartOutlined /> Health Monitoring</h1>
        <Button 
          type="primary" 
          icon={<ReloadOutlined />}
          onClick={fetchServers}
          loading={loading}
        >
          Refresh
        </Button>
      </div>

      <Card title="Server Health Status">
        <Table 
          dataSource={servers} 
          columns={columns} 
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 15 }}
        />
      </Card>

      <Modal
        title="Server Health Details"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={700}
      >
        {selectedServer && (
          <div>
            <Descriptions title="Server Information" bordered>
              <Descriptions.Item label="Hostname" span={2}>
                {selectedServer.server.hostname}
              </Descriptions.Item>
              <Descriptions.Item label="IP Address" span={1}>
                {selectedServer.server.ip_address}
              </Descriptions.Item>
              <Descriptions.Item label="Status" span={1}>
                <Tag color={getStatusColor(selectedServer.server.status)}>
                  {selectedServer.server.status.toUpperCase()}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Response Time" span={1}>
                {Math.round(selectedServer.server.response_time || 0)}ms
              </Descriptions.Item>
              <Descriptions.Item label="Last Check" span={1}>
                {selectedServer.server.last_check ? 
                  new Date(selectedServer.server.last_check).toLocaleString() : 
                  'Never'
                }
              </Descriptions.Item>
            </Descriptions>

            <div style={{ marginTop: 24 }}>
              <h3>Recent Health Checks</h3>
              <Table
                dataSource={selectedServer.recent_checks}
                size="small"
                pagination={false}
                columns={[
                  {
                    title: 'Type',
                    dataIndex: 'check_type',
                    key: 'check_type',
                  },
                  {
                    title: 'Status',
                    dataIndex: 'status',
                    key: 'status',
                    render: (status) => (
                      <Tag color={getStatusColor(status)} size="small">
                        {status.toUpperCase()}
                      </Tag>
                    ),
                  },
                  {
                    title: 'Response Time',
                    dataIndex: 'response_time',
                    key: 'response_time',
                    render: (time) => `${Math.round(time || 0)}ms`,
                  },
                  {
                    title: 'Time',
                    dataIndex: 'created_at',
                    key: 'created_at',
                    render: (time) => new Date(time).toLocaleTimeString(),
                  },
                ]}
              />
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}

export default HealthMonitoring;
