import React, { useState } from 'react';
import { Card, Form, Input, Select, Button, Space, message } from 'antd';

const { TextArea } = Input;
const { Option } = Select;

function NotificationPanel() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/notifications/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values)
      });
      
      if (response.ok) {
        message.success('Notification created successfully');
        form.resetFields();
      } else {
        message.error('Failed to create notification');
      }
    } catch (error) {
      message.error('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title="Create Notification">
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          priority: 'normal',
          notification_type: 'info'
        }}
      >
        <Form.Item 
          label="User ID" 
          name="user_id"
          rules={[{ required: true, message: 'Please enter user ID' }]}
        >
          <Input placeholder="Enter user ID" />
        </Form.Item>

        <Form.Item 
          label="Message" 
          name="message"
          rules={[{ required: true, message: 'Please enter message' }]}
        >
          <TextArea rows={4} placeholder="Enter notification message" />
        </Form.Item>

        <Form.Item label="Priority" name="priority">
          <Select>
            <Option value="critical">Critical</Option>
            <Option value="normal">Normal</Option>
            <Option value="low">Low</Option>
          </Select>
        </Form.Item>

        <Form.Item label="Type" name="notification_type">
          <Select>
            <Option value="info">Info</Option>
            <Option value="warning">Warning</Option>
            <Option value="error">Error</Option>
            <Option value="success">Success</Option>
          </Select>
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>
            Create Notification
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
}

export default NotificationPanel;
