import React, { useState } from 'react';
import { Card, Form, Input, Button, Table, Tag, Spin } from 'antd';
import { RadarChartOutlined, DesktopOutlined } from '@ant-design/icons';

function NetworkDiscovery() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [discoveredServers, setDiscoveredServers] = useState([]);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const response = await fetch('/api/validation/discover-network', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });
      
      const data = await response.json();
      setDiscoveredServers(data.discovered_servers || []);
    } catch (error) {
      console.error('Discovery failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: 'IP Address',
      dataIndex: 'ip',
      key: 'ip',
    },
    {
      title: 'Hostname',
      dataIndex: 'hostname',
      key: 'hostname',
      render: (hostname) => hostname || 'Unknown',
    },
    {
      title: 'Open Ports',
      dataIndex: 'open_ports',
      key: 'open_ports',
      render: (ports) => (
        <div>
          {ports.map(port => (
            <Tag key={port} color="blue">{port}</Tag>
          ))}
        </div>
      ),
    },
  ];

  return (
    <div>
      <h1><RadarChartOutlined /> Network Discovery</h1>
      
      <Card title="Discover Network Range" style={{ marginBottom: 24 }}>
        <Form
          form={form}
          layout="inline"
          onFinish={onFinish}
          style={{ width: '100%' }}
        >
          <Form.Item
            name="network_range"
            rules={[{ required: true, message: 'Please enter network range' }]}
            style={{ flex: 1 }}
          >
            <Input 
              placeholder="192.168.1.0/24" 
              addonBefore={<DesktopOutlined />}
            />
          </Form.Item>
          
          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
              icon={<RadarChartOutlined />}
            >
              Scan Network
            </Button>
          </Form.Item>
        </Form>
      </Card>

      <Card title={`Discovered Servers (${discoveredServers.length})`}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <Spin size="large" />
            <div style={{ marginTop: 16 }}>Scanning network...</div>
          </div>
        ) : (
          <Table 
            dataSource={discoveredServers} 
            columns={columns} 
            rowKey="ip"
            pagination={{ pageSize: 10 }}
          />
        )}
      </Card>
    </div>
  );
}

export default NetworkDiscovery;
