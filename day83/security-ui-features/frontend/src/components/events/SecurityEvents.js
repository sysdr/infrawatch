import React, { useState, useEffect } from 'react';
import { 
  Table, 
  Card, 
  Tag, 
  Button, 
  Space, 
  Select, 
  DatePicker, 
  Input,
  Modal,
  Descriptions,
  message
} from 'antd';
import { 
  ReloadOutlined, 
  EyeOutlined, 
  CheckCircleOutlined,
  SearchOutlined
} from '@ant-design/icons';
import { securityApi } from '../../services/api';

const { RangePicker } = DatePicker;
const { Option } = Select;

function SecurityEvents() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({});
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20 });

  useEffect(() => {
    loadEvents();
  }, [filters, pagination.current]);

  const loadEvents = async () => {
    setLoading(true);
    try {
      const response = await securityApi.getEvents({
        skip: (pagination.current - 1) * pagination.pageSize,
        limit: pagination.pageSize,
        ...filters
      });
      setEvents(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading events:', error);
      message.error('Failed to load security events');
      setLoading(false);
    }
  };

  const handleResolveEvent = async (eventId) => {
    try {
      await securityApi.resolveEvent(eventId, 'admin_user');
      message.success('Event resolved successfully');
      loadEvents();
    } catch (error) {
      console.error('Error resolving event:', error);
      message.error('Failed to resolve event');
    }
  };

  const columns = [
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      width: 100,
      render: (severity) => (
        <Tag color={
          severity === 'CRITICAL' ? 'red' :
          severity === 'HIGH' ? 'orange' :
          severity === 'MEDIUM' ? 'gold' : 'green'
        }>
          {severity}
        </Tag>
      ),
    },
    {
      title: 'Event Type',
      dataIndex: 'event_type',
      key: 'event_type',
      width: 200,
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: 'User',
      dataIndex: 'user_id',
      key: 'user_id',
      width: 120,
    },
    {
      title: 'IP Address',
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 150,
    },
    {
      title: 'Threat Score',
      dataIndex: 'threat_score',
      key: 'threat_score',
      width: 120,
      render: (score) => (
        <Tag color={score >= 80 ? 'red' : score >= 50 ? 'orange' : 'green'}>
          {score}
        </Tag>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'is_resolved',
      key: 'is_resolved',
      width: 100,
      render: (resolved) => (
        <Tag color={resolved ? 'green' : 'orange'}>
          {resolved ? 'Resolved' : 'Active'}
        </Tag>
      ),
    },
    {
      title: 'Time',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (time) => new Date(time).toLocaleString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => {
              setSelectedEvent(record);
              setModalVisible(true);
            }}
          >
            View
          </Button>
          {!record.is_resolved && (
            <Button
              type="link"
              icon={<CheckCircleOutlined />}
              onClick={() => handleResolveEvent(record.event_id)}
            >
              Resolve
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card 
        title="Security Events Explorer"
        extra={
          <Button icon={<ReloadOutlined />} onClick={loadEvents}>
            Refresh
          </Button>
        }
      >
        {/* Filters */}
        <Space style={{ marginBottom: 16 }} wrap>
          <Select
            placeholder="Severity"
            style={{ width: 150 }}
            allowClear
            onChange={(value) => setFilters({ ...filters, severity: value })}
          >
            <Option value="CRITICAL">Critical</Option>
            <Option value="HIGH">High</Option>
            <Option value="MEDIUM">Medium</Option>
            <Option value="LOW">Low</Option>
          </Select>
          
          <Input
            placeholder="Event Type"
            prefix={<SearchOutlined />}
            style={{ width: 200 }}
            allowClear
            onChange={(e) => setFilters({ ...filters, event_type: e.target.value })}
          />

          <Input
            placeholder="User ID"
            style={{ width: 150 }}
            allowClear
            onChange={(e) => setFilters({ ...filters, user_id: e.target.value })}
          />

          <Select
            placeholder="Status"
            style={{ width: 150 }}
            allowClear
            onChange={(value) => setFilters({ ...filters, is_resolved: value })}
          >
            <Option value={false}>Active</Option>
            <Option value={true}>Resolved</Option>
          </Select>
        </Space>

        <Table
          columns={columns}
          dataSource={events}
          loading={loading}
          rowKey="id"
          pagination={{
            ...pagination,
            onChange: (page) => setPagination({ ...pagination, current: page }),
          }}
        />
      </Card>

      {/* Event Details Modal */}
      <Modal
        title="Event Details"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        width={800}
        footer={[
          <Button key="close" onClick={() => setModalVisible(false)}>
            Close
          </Button>,
          selectedEvent && !selectedEvent.is_resolved && (
            <Button 
              key="resolve" 
              type="primary"
              onClick={() => {
                handleResolveEvent(selectedEvent.event_id);
                setModalVisible(false);
              }}
            >
              Mark as Resolved
            </Button>
          ),
        ]}
      >
        {selectedEvent && (
          <Descriptions column={2} bordered>
            <Descriptions.Item label="Event ID" span={2}>
              {selectedEvent.event_id}
            </Descriptions.Item>
            <Descriptions.Item label="Event Type">
              {selectedEvent.event_type}
            </Descriptions.Item>
            <Descriptions.Item label="Severity">
              <Tag color={
                selectedEvent.severity === 'CRITICAL' ? 'red' :
                selectedEvent.severity === 'HIGH' ? 'orange' :
                selectedEvent.severity === 'MEDIUM' ? 'gold' : 'green'
              }>
                {selectedEvent.severity}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="User ID">
              {selectedEvent.user_id}
            </Descriptions.Item>
            <Descriptions.Item label="IP Address">
              {selectedEvent.ip_address}
            </Descriptions.Item>
            <Descriptions.Item label="Threat Score" span={2}>
              <Tag color={selectedEvent.threat_score >= 80 ? 'red' : selectedEvent.threat_score >= 50 ? 'orange' : 'green'}>
                {selectedEvent.threat_score} / 100
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Description" span={2}>
              {selectedEvent.description}
            </Descriptions.Item>
            <Descriptions.Item label="Source">
              {selectedEvent.source}
            </Descriptions.Item>
            <Descriptions.Item label="Status">
              <Tag color={selectedEvent.is_resolved ? 'green' : 'orange'}>
                {selectedEvent.is_resolved ? 'Resolved' : 'Active'}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Created At" span={2}>
              {new Date(selectedEvent.created_at).toLocaleString()}
            </Descriptions.Item>
            {selectedEvent.metadata && (
              <Descriptions.Item label="Metadata" span={2}>
                <pre>{JSON.stringify(selectedEvent.metadata, null, 2)}</pre>
              </Descriptions.Item>
            )}
          </Descriptions>
        )}
      </Modal>
    </div>
  );
}

export default SecurityEvents;
