import React, { useState, useEffect } from 'react';
import { Card, Button, List, Modal, Form, Input, message, Tag } from 'antd';
import { PlusOutlined, TeamOutlined } from '@ant-design/icons';
import { teamAPI } from '../services/api';

function TeamManagement() {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    setLoading(true);
    try {
      const response = await teamAPI.getAll();
      setTeams(response.data);
    } catch (error) {
      message.error('Failed to fetch teams');
    }
    setLoading(false);
  };

  const handleCreate = async (values) => {
    try {
      await teamAPI.create(values);
      message.success('Team created successfully');
      setModalVisible(false);
      form.resetFields();
      fetchTeams();
    } catch (error) {
      message.error('Failed to create team');
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Team Management</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          Create Team
        </Button>
      </div>

      <List
        grid={{ gutter: 16, xs: 1, sm: 2, md: 2, lg: 3, xl: 3, xxl: 4 }}
        dataSource={teams}
        loading={loading}
        renderItem={(team) => (
          <List.Item>
            <Card
              hoverable
              actions={[
                <TeamOutlined key="members" />,
              ]}
            >
              <Card.Meta
                title={team.name}
                description={team.description || 'No description'}
              />
              <div style={{ marginTop: 16 }}>
                <Tag color="blue">Team</Tag>
              </div>
            </Card>
          </List.Item>
        )}
      />

      <Modal
        title="Create Team"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item 
            name="name" 
            label="Team Name" 
            rules={[{ required: true, message: 'Please enter a team name' }]}
            tooltip="Enter a name for the team"
          >
            <Input />
          </Form.Item>
          <Form.Item 
            name="description" 
            label="Description"
            tooltip="Optional description for the team"
          >
            <Input.TextArea rows={4} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              Create Team
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default TeamManagement;
