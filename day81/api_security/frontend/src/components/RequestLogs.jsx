import React, { useState, useEffect } from 'react';
import { Table, Tag, Space, Input, Select, Button, Tooltip } from 'antd';
import { SearchOutlined, ReloadOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { requestLogService } from '../services/api';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

const { Search } = Input;
const { Option } = Select;

function RequestLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterKeyId, setFilterKeyId] = useState(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const response = await requestLogService.getLogs(0, 100, filterKeyId);
      setLogs(response.data);
    } catch (error) {
      console.error('Failed to fetch logs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000); // Auto-refresh every 5s
    return () => clearInterval(interval);
  }, [filterKeyId]);

  const getStatusColor = (code) => {
    if (code >= 200 && code < 300) return 'success';
    if (code >= 400 && code < 500) return 'warning';
    if (code >= 500) return 'error';
    return 'default';
  };

  const columns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (date) => (
        <Tooltip title={dayjs(date).format('YYYY-MM-DD HH:mm:ss')}>
          <span>{dayjs(date).fromNow()}</span>
        </Tooltip>
      ),
      width: 120
    },
    {
      title: 'Method',
      dataIndex: 'method',
      key: 'method',
      render: (method) => {
        const colors = {
          GET: 'blue',
          POST: 'green',
          PUT: 'orange',
          DELETE: 'red',
          PATCH: 'purple'
        };
        return <Tag color={colors[method] || 'default'}>{method}</Tag>;
      },
      width: 80
    },
    {
      title: 'Path',
      dataIndex: 'path',
      key: 'path',
      ellipsis: true
    },
    {
      title: 'Source IP',
      dataIndex: 'source_ip',
      key: 'source_ip',
      render: (ip) => <code>{ip}</code>,
      width: 140
    },
    {
      title: 'Status',
      dataIndex: 'status_code',
      key: 'status_code',
      render: (code) => (
        <Tag color={getStatusColor(code)}>{code}</Tag>
      ),
      width: 80
    },
    {
      title: 'Security',
      key: 'security',
      render: (_, record) => (
        <Space size={[0, 4]} wrap>
          <Tooltip title="Signature Valid">
            <Tag 
              color={record.signature_valid ? 'success' : 'error'}
              icon={record.signature_valid ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
            >
              Sig
            </Tag>
          </Tooltip>
          <Tooltip title="IP Whitelisted">
            <Tag 
              color={record.ip_whitelisted ? 'success' : 'warning'}
              icon={record.ip_whitelisted ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
            >
              IP
            </Tag>
          </Tooltip>
          {record.rate_limited && (
            <Tag color="error">Rate Limited</Tag>
          )}
        </Space>
      ),
      width: 150
    },
    {
      title: 'Response Time',
      dataIndex: 'response_time_ms',
      key: 'response_time_ms',
      render: (time) => {
        const color = time < 100 ? 'success' : time < 500 ? 'warning' : 'error';
        return <Tag color={color}>{time}ms</Tag>;
      },
      width: 120
    },
    {
      title: 'API Key',
      dataIndex: 'api_key_id',
      key: 'api_key_id',
      render: (keyId) => (
        <Tooltip title={keyId}>
          <code style={{ fontSize: '11px' }}>{keyId.substring(0, 8)}...</code>
        </Tooltip>
      ),
      width: 100
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Request Logs</h2>
        <Space>
          <Search
            placeholder="Filter by API Key ID"
            allowClear
            onSearch={(value) => setFilterKeyId(value || null)}
            style={{ width: 250 }}
            prefix={<SearchOutlined />}
          />
          <Button 
            icon={<ReloadOutlined />}
            onClick={fetchLogs}
          >
            Refresh
          </Button>
        </Space>
      </div>

      <Table 
        columns={columns} 
        dataSource={logs} 
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 20 }}
        size="small"
        scroll={{ x: 1200 }}
      />
    </div>
  );
}

export default RequestLogs;
