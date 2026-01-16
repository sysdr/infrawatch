import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, InputNumber, Tag, Space, message, Card, Tooltip, Typography } from 'antd';
import { PlusOutlined, DeleteOutlined, SyncOutlined, CopyOutlined, EyeOutlined, EyeInvisibleOutlined } from '@ant-design/icons';
import { apiKeyService } from '../services/api';
import dayjs from 'dayjs';

const { TextArea } = Input;
const { Text, Paragraph } = Typography;

function APIKeyManagement() {
  const [keys, setKeys] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [newKeyData, setNewKeyData] = useState(null);
  const [showFullKey, setShowFullKey] = useState({});
  const [form] = Form.useForm();

  const fetchKeys = async () => {
    setLoading(true);
    try {
      const response = await apiKeyService.listKeys();
      setKeys(response.data);
    } catch (error) {
      message.error('Failed to fetch API keys');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKeys();
  }, []);

  const handleCreateKey = async (values) => {
    try {
      const ipWhitelist = values.ip_whitelist 
        ? values.ip_whitelist.split('\n').filter(ip => ip.trim())
        : [];
      
      const response = await apiKeyService.createKey({
        ...values,
        ip_whitelist: ipWhitelist
      });
      
      setNewKeyData(response.data);
      message.success('API key created successfully');
      form.resetFields();
      fetchKeys();
    } catch (error) {
      message.error('Failed to create API key');
    }
  };

  const handleRevokeKey = async (keyId) => {
    Modal.confirm({
      title: 'Revoke API Key',
      content: 'Are you sure you want to revoke this API key? This action cannot be undone.',
      okText: 'Revoke',
      okType: 'danger',
      onOk: async () => {
        try {
          await apiKeyService.revokeKey(keyId);
          message.success('API key revoked');
          fetchKeys();
        } catch (error) {
          message.error('Failed to revoke API key');
        }
      }
    });
  };

  const handleRotateKey = async (keyId) => {
    Modal.confirm({
      title: 'Rotate API Key',
      content: 'This will create a new key and schedule the old one for revocation in 24 hours.',
      okText: 'Rotate',
      onOk: async () => {
        try {
          const response = await apiKeyService.rotateKey(keyId);
          setNewKeyData(response.data);
          message.success('API key rotated successfully');
          fetchKeys();
        } catch (error) {
          message.error('Failed to rotate API key');
        }
      }
    });
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    message.success('Copied to clipboard');
  };

  const toggleKeyVisibility = (keyId) => {
    setShowFullKey(prev => ({ ...prev, [keyId]: !prev[keyId] }));
  };

  const maskKey = (key) => {
    const parts = key.split('_');
    if (parts.length === 3) {
      return `${parts[0]}_${parts[1]}_${'*'.repeat(20)}`;
    }
    return key;
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space direction="vertical" size={0}>
          <Text strong>{text}</Text>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {record.description}
          </Text>
        </Space>
      )
    },
    {
      title: 'Key ID',
      dataIndex: 'key_id',
      key: 'key_id',
      render: (text) => (
        <Space>
          <Text code>{text}</Text>
          <Tooltip title="Copy">
            <Button 
              type="text" 
              size="small" 
              icon={<CopyOutlined />}
              onClick={() => copyToClipboard(text)}
            />
          </Tooltip>
        </Space>
      )
    },
    {
      title: 'Rate Limit',
      key: 'rate_limit',
      render: (_, record) => (
        <Text>{record.rate_limit}/{record.rate_window}s</Text>
      )
    },
    {
      title: 'IP Whitelist',
      dataIndex: 'ip_whitelist',
      key: 'ip_whitelist',
      render: (whitelist) => (
        whitelist.length > 0 ? (
          <Space size={[0, 4]} wrap>
            {whitelist.slice(0, 2).map(ip => (
              <Tag key={ip} color="blue">{ip}</Tag>
            ))}
            {whitelist.length > 2 && <Tag>+{whitelist.length - 2} more</Tag>}
          </Space>
        ) : (
          <Text type="secondary">All IPs</Text>
        )
      )
    },
    {
      title: 'Status',
      key: 'status',
      render: (_, record) => (
        <Space>
          {record.is_active && !record.is_revoked && <Tag color="success">Active</Tag>}
          {record.is_revoked && <Tag color="error">Revoked</Tag>}
          {record.expires_at && new Date(record.expires_at) < new Date() && (
            <Tag color="warning">Expired</Tag>
          )}
        </Space>
      )
    },
    {
      title: 'Last Used',
      dataIndex: 'last_used_at',
      key: 'last_used_at',
      render: (date) => date ? dayjs(date).fromNow() : 'Never'
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Tooltip title="Rotate Key">
            <Button 
              type="text" 
              icon={<SyncOutlined />}
              onClick={() => handleRotateKey(record.key_id)}
              disabled={record.is_revoked}
            />
          </Tooltip>
          <Tooltip title="Revoke Key">
            <Button 
              type="text" 
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleRevokeKey(record.key_id)}
              disabled={record.is_revoked}
            />
          </Tooltip>
        </Space>
      )
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>API Key Management</h2>
        <Button 
          type="primary" 
          icon={<PlusOutlined />}
          onClick={() => setModalVisible(true)}
        >
          Create New Key
        </Button>
      </div>

      <Table 
        columns={columns} 
        dataSource={keys} 
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title="Create New API Key"
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setNewKeyData(null);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        {!newKeyData ? (
          <Form
            form={form}
            layout="vertical"
            onFinish={handleCreateKey}
            initialValues={{
              rate_limit: 100,
              rate_window: 60,
              expires_in_days: 90
            }}
          >
            <Form.Item
              label="Key Name"
              name="name"
              rules={[{ required: true, message: 'Please enter key name' }]}
            >
              <Input placeholder="Production API Key" />
            </Form.Item>

            <Form.Item
              label="Description"
              name="description"
            >
              <TextArea rows={2} placeholder="Optional description" />
            </Form.Item>

            <Form.Item
              label="Rate Limit (requests)"
              name="rate_limit"
              rules={[{ required: true }]}
            >
              <InputNumber min={1} max={10000} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              label="Rate Window (seconds)"
              name="rate_window"
              rules={[{ required: true }]}
            >
              <InputNumber min={1} max={3600} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              label="IP Whitelist (one CIDR per line)"
              name="ip_whitelist"
              tooltip="Leave empty to allow all IPs. Example: 192.168.1.0/24"
            >
              <TextArea 
                rows={3} 
                placeholder="192.168.1.0/24&#10;10.0.0.0/8"
              />
            </Form.Item>

            <Form.Item
              label="Expires In (days)"
              name="expires_in_days"
            >
              <InputNumber min={1} max={365} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item>
              <Space>
                <Button type="primary" htmlType="submit">
                  Create Key
                </Button>
                <Button onClick={() => setModalVisible(false)}>
                  Cancel
                </Button>
              </Space>
            </Form.Item>
          </Form>
        ) : (
          <Card>
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <div>
                <Text strong>API Key Created Successfully!</Text>
                <br />
                <Text type="warning">
                  ⚠️ Store this key securely. It won't be shown again.
                </Text>
              </div>
              
              <div>
                <Text strong>Full API Key:</Text>
                <br />
                <Space style={{ width: '100%', marginTop: 8 }}>
                  <Input.Password
                    value={newKeyData.full_key}
                    readOnly
                    style={{ fontFamily: 'monospace', width: '400px' }}
                    iconRender={visible => (visible ? <EyeOutlined /> : <EyeInvisibleOutlined />)}
                  />
                  <Button 
                    icon={<CopyOutlined />}
                    onClick={() => copyToClipboard(newKeyData.full_key)}
                  >
                    Copy
                  </Button>
                </Space>
              </div>

              <div>
                <Text strong>Key Details:</Text>
                <br />
                <Text>Name: {newKeyData.api_key.name}</Text>
                <br />
                <Text>Key ID: {newKeyData.api_key.key_id}</Text>
                <br />
                <Text>Rate Limit: {newKeyData.api_key.rate_limit}/{newKeyData.api_key.rate_window}s</Text>
              </div>

              {newKeyData.warning && (
                <Text type="warning">{newKeyData.warning}</Text>
              )}

              <Button 
                type="primary" 
                block
                onClick={() => {
                  setModalVisible(false);
                  setNewKeyData(null);
                }}
              >
                Close
              </Button>
            </Space>
          </Card>
        )}
      </Modal>
    </div>
  );
}

export default APIKeyManagement;
