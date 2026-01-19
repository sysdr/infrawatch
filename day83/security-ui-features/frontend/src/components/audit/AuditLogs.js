import React, { useState, useEffect } from 'react';
import { Table, Card, Tag, Button, Space, Select, Input, DatePicker } from 'antd';
import { ReloadOutlined, SearchOutlined } from '@ant-design/icons';
import { securityApi } from '../../services/api';

const { RangePicker } = DatePicker;
const { Option } = Select;

function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({});
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20 });

  useEffect(() => {
    loadLogs();
  }, [filters, pagination.current]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const response = await securityApi.getAuditLogs({
        skip: (pagination.current - 1) * pagination.pageSize,
        limit: pagination.pageSize,
        ...filters
      });
      setLogs(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading audit logs:', error);
      setLoading(false);
    }
  };

  const columns = [
    {
      title: 'Time',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (time) => new Date(time).toLocaleString(),
    },
    {
      title: 'Action',
      dataIndex: 'action_type',
      key: 'action_type',
      width: 200,
    },
    {
      title: 'Actor',
      dataIndex: 'actor',
      key: 'actor',
      width: 150,
    },
    {
      title: 'Resource Type',
      dataIndex: 'resource_type',
      key: 'resource_type',
      width: 150,
    },
    {
      title: 'Resource ID',
      dataIndex: 'resource_id',
      key: 'resource_id',
      width: 150,
    },
    {
      title: 'Result',
      dataIndex: 'action_result',
      key: 'action_result',
      width: 100,
      render: (result) => (
        <Tag color={result === 'success' ? 'green' : 'red'}>
          {result.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'IP Address',
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 150,
    },
  ];

  return (
    <Card 
      title="Audit Logs"
      extra={
        <Button icon={<ReloadOutlined />} onClick={loadLogs}>
          Refresh
        </Button>
      }
    >
      <Space style={{ marginBottom: 16 }} wrap>
        <Input
          placeholder="Action Type"
          prefix={<SearchOutlined />}
          style={{ width: 200 }}
          allowClear
          onChange={(e) => setFilters({ ...filters, action_type: e.target.value })}
        />

        <Input
          placeholder="Actor"
          style={{ width: 150 }}
          allowClear
          onChange={(e) => setFilters({ ...filters, actor: e.target.value })}
        />

        <Select
          placeholder="Result"
          style={{ width: 150 }}
          allowClear
          onChange={(value) => setFilters({ ...filters, action_result: value })}
        >
          <Option value="success">Success</Option>
          <Option value="failure">Failure</Option>
        </Select>
      </Space>

      <Table
        columns={columns}
        dataSource={logs}
        loading={loading}
        rowKey="id"
        pagination={{
          ...pagination,
          onChange: (page) => setPagination({ ...pagination, current: page }),
        }}
      />
    </Card>
  );
}

export default AuditLogs;
