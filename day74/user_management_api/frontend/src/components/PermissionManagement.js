import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, message, Space, Descriptions, Select, Table, Tag, Tabs, Modal } from 'antd';
import { SafetyOutlined, CheckCircleOutlined, CloseCircleOutlined, PlusOutlined, CheckOutlined } from '@ant-design/icons';
import { permissionAPI, userAPI } from '../services/api';

const { Option } = Select;

function PermissionManagement() {
  const [checkResult, setCheckResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [assignLoading, setAssignLoading] = useState(false);
  const [users, setUsers] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [userPermissions, setUserPermissions] = useState([]);
  const [userOptions, setUserOptions] = useState([]);
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [usersLoading, setUsersLoading] = useState(true);
  const [assignForm] = Form.useForm();
  const [checkForm] = Form.useForm();
  const [assignModalVisible, setAssignModalVisible] = useState(false);

  useEffect(() => {
    fetchUsers();
    fetchPermissions();
  }, []);

  useEffect(() => {
    if (selectedUserId) {
      fetchUserPermissions(selectedUserId);
    }
  }, [selectedUserId]);

  const fetchUsers = async () => {
    setUsersLoading(true);
    try {
      const response = await userAPI.getAll({ page: 1, page_size: 100 });
      const userList = response.data.users || [];
      setUsers(userList);
      // Map users to options for Select component - filter out invalid UUIDs
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
      const options = userList
        .filter(user => user.id && uuidRegex.test(user.id))
        .map(user => ({
          value: user.id,
          label: `${user.username} (${user.email})`,
          key: user.id
        }));
      setUserOptions(options);
      
      if (options.length === 0) {
        message.warning('No users found in the system. Please create users first.');
      }
    } catch (error) {
      console.error('Failed to fetch users:', error);
      message.error('Failed to load users. Please refresh the page or check your connection.');
    } finally {
      setUsersLoading(false);
    }
  };

  const fetchPermissions = async () => {
    try {
      const response = await permissionAPI.getAll();
      setPermissions(response.data || []);
    } catch (error) {
      console.error('Failed to fetch permissions:', error);
      message.error('Failed to load permissions');
    }
  };

  const fetchUserPermissions = async (userId) => {
    try {
      const response = await permissionAPI.getUserPermissions(userId);
      setUserPermissions(response.data.permissions || []);
    } catch (error) {
      console.error('Failed to fetch user permissions:', error);
      setUserPermissions([]);
    }
  };

  const handleUserSearch = async (searchValue) => {
    if (!searchValue || searchValue.length < 1) {
      // If empty, show all users - filter out invalid UUIDs
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
      const options = users
        .filter(user => user.id && uuidRegex.test(user.id))
        .map(user => ({
          value: user.id,
          label: `${user.username} (${user.email})`,
          key: user.id
        }));
      setUserOptions(options);
      return;
    }
    
    setSearchLoading(true);
    try {
      const response = await userAPI.search({ q: searchValue });
      const searchResults = response.data.users || [];
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
      const options = searchResults
        .filter(user => user.id && uuidRegex.test(user.id))
        .map(user => ({
          value: user.id,
          label: `${user.username} (${user.email})`,
          key: user.id
        }));
      setUserOptions(options);
    } catch (error) {
      console.error('Search failed:', error);
      message.error('User search failed');
    }
    setSearchLoading(false);
  };

  const handleCheckPermission = async (values) => {
    // Comprehensive validation before API call
    if (!values.user_id) {
      message.error('Please select a user');
      return;
    }

    // Strict UUID validation - backend requires valid UUID format
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    const userId = String(values.user_id).trim();
    
    if (!uuidRegex.test(userId)) {
      message.error('Invalid user ID format. Please select a valid user from the dropdown.');
      // Clear invalid value from form
      checkForm.setFieldsValue({ user_id: undefined });
      setCheckResult(null);
      return;
    }

    if (!values.resource || !values.action) {
      message.error('Please select both resource and action');
      return;
    }
    
    // Prevent duplicate submissions
    if (loading) {
      return;
    }
    
    setLoading(true);
    setCheckResult(null); // Clear previous result
    
    try {
      // Ensure we're sending the correct data format
      const requestPayload = {
        resource: String(values.resource).trim(),
        action: String(values.action).trim(),
      };
      
      // Log request for debugging (remove in production)
      if (process.env.NODE_ENV === 'development') {
        console.log('Permission check request:', {
          userId,
          payload: requestPayload,
          url: `/api/permissions/users/${userId}/check`
        });
      }
      
      const response = await permissionAPI.checkPermission(userId, requestPayload);
      setCheckResult(response.data);
      
      // Refresh user permissions after successful check
      if (userId) {
        fetchUserPermissions(userId);
      }
    } catch (error) {
      console.error('Permission check error:', error);
      
      // Handle different error types
      if (error.response) {
        const { status, data } = error.response;
        
        if (status === 422) {
          // Validation error from backend
          const detail = data?.detail;
          if (Array.isArray(detail)) {
            const uuidError = detail.find(
              err => err.msg?.includes('UUID') || 
                     err.type === 'uuid_parsing' || 
                     err.loc?.includes('user_id')
            );
            if (uuidError) {
              message.error('Invalid user ID format. The selected user ID is not valid. Please select a different user.');
              checkForm.setFieldsValue({ user_id: undefined });
            } else {
              const resourceError = detail.find(err => err.loc?.includes('resource'));
              const actionError = detail.find(err => err.loc?.includes('action'));
              if (resourceError || actionError) {
                message.error('Invalid resource or action. Please select valid values.');
              } else {
                message.error(detail[0]?.msg || 'Validation failed. Please check your input.');
              }
            }
          } else if (typeof detail === 'string') {
            if (detail.includes('UUID') || detail.includes('uuid')) {
              message.error('Invalid user ID format. Please select a valid user from the dropdown.');
              checkForm.setFieldsValue({ user_id: undefined });
            } else {
              message.error(detail);
            }
          } else {
            message.error('Validation error. Please check your input.');
          }
        } else if (status === 404) {
          message.error('User not found. Please select a different user.');
        } else if (status >= 500) {
          message.error('Server error. Please try again later.');
        } else {
          message.error(data?.detail || data?.message || 'Permission check failed');
        }
      } else if (error.request) {
        message.error('Network error. Please check your connection and try again.');
      } else {
        message.error('An unexpected error occurred. Please try again.');
      }
      
      setCheckResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleAssignPermission = async (values) => {
    if (!values.user_id) {
      message.error('Please select a user');
      return;
    }
    if (!values.permission_id) {
      message.error('Please select a permission');
      return;
    }

    // Validate UUID format
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(values.user_id)) {
      message.error('Invalid user ID format. Please select a valid user from the dropdown.');
      return;
    }
    if (!uuidRegex.test(values.permission_id)) {
      message.error('Invalid permission ID format. Please select a valid permission from the dropdown.');
      return;
    }

    setAssignLoading(true);
    try {
      await permissionAPI.assignToUser(values.user_id, {
        permission_id: values.permission_id,
      });
      message.success('Permission assigned successfully!');
      setAssignModalVisible(false);
      assignForm.resetFields();
      // Refresh user permissions
      fetchUserPermissions(values.user_id);
      setSelectedUserId(values.user_id);
    } catch (error) {
      console.error('Permission assignment error:', error);
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === 'string' && detail.includes('already assigned')) {
          message.warning('This permission is already assigned to the user');
        } else {
          message.error(typeof detail === 'string' ? detail : 'Failed to assign permission');
        }
      } else {
        message.error('Failed to assign permission');
      }
    }
    setAssignLoading(false);
  };

  const handleUserSelect = (userId) => {
    setSelectedUserId(userId);
    // Clear previous check result when user changes
    setCheckResult(null);
    if (userId) {
      fetchUserPermissions(userId);
    } else {
      setUserPermissions([]);
    }
  };

  const permissionColumns = [
    {
      title: 'Permission',
      dataIndex: 'permission',
      key: 'permission',
      render: (permission) => <Tag color="blue">{permission}</Tag>,
    },
  ];

  const tabItems = [
    {
      key: 'check',
      label: 'Check Permission',
      children: (
          <Card 
            title={
              <div>
                <SafetyOutlined style={{ marginRight: 8, color: '#1890ff' }} />
                Check User Permission
              </div>
            }
            extra={
              <Button 
                type="link" 
                icon={<SafetyOutlined />}
                onClick={() => {
                  setCheckResult(null);
                  checkForm.resetFields();
                  message.info('Form reset. You can now check a different permission.');
                }}
              >
                Clear Form
              </Button>
            }
          >
            {/* Help Instructions */}
            <div style={{ marginBottom: 24, padding: 16, background: '#e6f7ff', border: '1px solid #91d5ff', borderRadius: 4 }}>
              <div style={{ marginBottom: 12, fontWeight: 600, color: '#0958d9', fontSize: '14px' }}>
                📖 How to Check Permissions - Step by Step:
              </div>
              <ol style={{ margin: 0, paddingLeft: 20, fontSize: '13px', color: '#262626', lineHeight: '1.8' }}>
                <li><strong>User ID:</strong> Click the dropdown below and <strong>select a user</strong> from the list (e.g., "user1 (user1@example.com)"). You can type to search. <span style={{ color: '#ff4d4f' }}>⚠️ DO NOT type the UUID manually!</span></li>
                <li><strong>Resource:</strong> Select the resource type (e.g., "users", "teams", "reports", "permissions", "activity")</li>
                <li><strong>Action:</strong> Select the action (e.g., "read", "write", "delete", or "*" for all actions)</li>
                <li><strong>Check:</strong> Click the "Check Permission" button to see if the user has the permission</li>
              </ol>
              <div style={{ marginTop: 12, padding: 8, background: '#fff', borderRadius: 4, fontSize: '12px', color: '#595959' }}>
                <strong>💡 Tip:</strong> Make sure the user has been assigned the permission first using the "Assign Permission" tab. If the check fails, you'll see a detailed message explaining why.
              </div>
            </div>
            
            {usersLoading && userOptions.length === 0 && (
              <div style={{ marginBottom: 16, padding: 16, background: '#f0f2f5', borderRadius: 4 }}>
                <Space>
                  <span>⏳ Loading users from database...</span>
                </Space>
              </div>
            )}
            
            {!usersLoading && userOptions.length === 0 && (
              <div style={{ marginBottom: 16, padding: 16, background: '#fff7e6', border: '1px solid #ffd591', borderRadius: 4 }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div><strong style={{ color: '#fa8c16' }}>⚠️ No Users Available</strong></div>
                  <div style={{ fontSize: '13px', color: '#666' }}>
                    You need to create users first before checking permissions. Go to the <strong>"Users"</strong> tab in the left menu to create users, then come back here to check permissions.
                  </div>
                </Space>
              </div>
            )}
            
            <Form form={checkForm} onFinish={handleCheckPermission} layout="vertical">
              <Form.Item 
                name="user_id" 
                label="User ID"
                tooltip="Select a user from the dropdown. You can type to search by username or email, but you must select from the dropdown. Do not type UUIDs manually."
                rules={[
                  { required: true, message: 'Please select a user from the dropdown' },
                  {
                    validator: (_, value) => {
                      if (!value) {
                        return Promise.resolve();
                      }
                      // Strict UUID validation - backend requires valid UUID format
                      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
                      if (!uuidRegex.test(String(value).trim())) {
                        return Promise.reject(new Error('Invalid format. Please select a user from the dropdown'));
                      }
                      return Promise.resolve();
                    },
                  },
                ]}
                extra={
                  userOptions.length === 0 ? (
                    <span style={{ color: '#ff4d4f', fontSize: '12px' }}>
                      No users loaded. Please refresh the page or check if users exist in the system. Go to the "Users" tab to create users first.
                    </span>
                  ) : (
                    <span style={{ color: '#666', fontSize: '12px' }}>
                      Select from dropdown - DO NOT type manually. Currently {userOptions.length} user(s) available.
                    </span>
                  )
                }
              >
                <Select
                  showSearch
                  placeholder={usersLoading ? "Loading users..." : "Select a user from dropdown"}
                  optionFilterProp="label"
                  filterOption={false}
                  onSearch={handleUserSearch}
                  onChange={(value) => {
                    // Clear previous check result when user changes
                    setCheckResult(null);
                    // Only handle user selection for display purposes
                    // Form.Item will handle the actual form field binding
                    handleUserSelect(value);
                    // Ensure form field is updated
                    checkForm.setFieldsValue({ user_id: value });
                  }}
                  loading={searchLoading || usersLoading}
                  disabled={false}
                  style={{ width: '100%' }}
                  allowClear
                  size="large"
                  notFoundContent={
                    usersLoading || searchLoading
                      ? <div style={{ padding: '12px', textAlign: 'center' }}>
                          <div>🔍 {usersLoading ? 'Loading users from database...' : 'Searching users...'}</div>
                        </div>
                      : userOptions.length === 0 
                        ? <div style={{ padding: '12px', textAlign: 'center' }}>
                            <div style={{ color: '#ff4d4f', marginBottom: '8px', fontWeight: 500 }}>❌ No users found in system</div>
                            <div style={{ fontSize: '12px', color: '#666', lineHeight: '1.6' }}>
                              Please create users first in the <strong>"Users"</strong> tab.<br/>
                              You cannot check permissions without users in the system.
                            </div>
                          </div>
                        : <div style={{ padding: '12px', textAlign: 'center' }}>
                            <div style={{ color: '#fa8c16', marginBottom: '8px', fontWeight: 500 }}>❌ No matching users found</div>
                            <div style={{ fontSize: '12px', color: '#666' }}>
                              Try searching with a different username or email address
                            </div>
                          </div>
                  }
                  getPopupContainer={(trigger) => trigger.parentElement}
                  dropdownRender={(menu) => (
                    <>
                      {menu}
                      {userOptions.length > 0 && !usersLoading && (
                        <div style={{ padding: '10px', borderTop: '1px solid #f0f0f0', fontSize: '12px', color: '#666', textAlign: 'center', background: '#fafafa' }}>
                          ✅ Showing {userOptions.length} user(s). Click to select one.
                        </div>
                      )}
                      {userOptions.length === 0 && !usersLoading && (
                        <div style={{ padding: '10px', borderTop: '1px solid #f0f0f0', fontSize: '12px', color: '#ff4d4f', textAlign: 'center', background: '#fff1f0' }}>
                          ⚠️ No users available. Please create users first in the "Users" tab.
                        </div>
                      )}
                    </>
                  )}
                >
                  {userOptions.length > 0 ? (
                    userOptions.map(option => (
                      <Option key={option.key} value={option.value} label={option.label}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div>
                            <div style={{ fontWeight: 500, color: '#262626' }}>{option.label.split(' (')[0]}</div>
                            <div style={{ fontSize: '11px', color: '#8c8c8c', marginTop: '2px' }}>{option.label.split('(')[1]?.replace(')', '')}</div>
                          </div>
                          <div style={{ fontSize: '10px', color: '#bfbfbf', fontFamily: 'monospace' }}>
                            UUID: {String(option.value).substring(0, 8)}...
                          </div>
                        </div>
                      </Option>
                    ))
                  ) : (
                    <Option disabled value="no-users" label="No users available">
                      <div style={{ color: '#999', textAlign: 'center', padding: '8px' }}>
                        No users found. Please create users first.
                      </div>
                    </Option>
                  )}
                </Select>
              </Form.Item>
              <Form.Item 
                name="resource" 
                label="Resource"
                tooltip="Select the resource type you want to check permission for"
                rules={[{ required: true, message: 'Please select a resource' }]}
                extra={<span style={{ color: '#666', fontSize: '12px' }}>Select what type of resource to check (e.g., users, teams, reports)</span>}
              >
                <Select 
                  placeholder="Select a resource (e.g., users, teams, reports)" 
                  allowClear
                  size="large"
                  showSearch
                  optionFilterProp="children"
                >
                  <Option value="users">
                    <div>
                      <div style={{ fontWeight: 500 }}>users</div>
                      <div style={{ fontSize: '11px', color: '#999' }}>User management resource</div>
                    </div>
                  </Option>
                  <Option value="teams">
                    <div>
                      <div style={{ fontWeight: 500 }}>teams</div>
                      <div style={{ fontSize: '11px', color: '#999' }}>Team management resource</div>
                    </div>
                  </Option>
                  <Option value="reports">
                    <div>
                      <div style={{ fontWeight: 500 }}>reports</div>
                      <div style={{ fontSize: '11px', color: '#999' }}>Reports resource</div>
                    </div>
                  </Option>
                  <Option value="permissions">
                    <div>
                      <div style={{ fontWeight: 500 }}>permissions</div>
                      <div style={{ fontSize: '11px', color: '#999' }}>Permission management resource</div>
                    </div>
                  </Option>
                  <Option value="activity">
                    <div>
                      <div style={{ fontWeight: 500 }}>activity</div>
                      <div style={{ fontSize: '11px', color: '#999' }}>Activity logs resource</div>
                    </div>
                  </Option>
                </Select>
              </Form.Item>
              <Form.Item 
                name="action" 
                label="Action"
                tooltip="Select the action you want to check permission for"
                rules={[{ required: true, message: 'Please select an action' }]}
                extra={<span style={{ color: '#666', fontSize: '12px' }}>Select what action to check (e.g., read, write, delete, or * for all actions)</span>}
              >
                <Select 
                  placeholder="Select an action (e.g., read, write, delete)" 
                  allowClear
                  size="large"
                  showSearch
                  optionFilterProp="children"
                >
                  <Option value="read">
                    <div>
                      <div style={{ fontWeight: 500 }}>read</div>
                      <div style={{ fontSize: '11px', color: '#999' }}>View/read access</div>
                    </div>
                  </Option>
                  <Option value="write">
                    <div>
                      <div style={{ fontWeight: 500 }}>write</div>
                      <div style={{ fontSize: '11px', color: '#999' }}>Create/update access</div>
                    </div>
                  </Option>
                  <Option value="delete">
                    <div>
                      <div style={{ fontWeight: 500 }}>delete</div>
                      <div style={{ fontSize: '11px', color: '#999' }}>Delete access</div>
                    </div>
                  </Option>
                  <Option value="*">
                    <div>
                      <div style={{ fontWeight: 500 }}>* (all actions)</div>
                      <div style={{ fontSize: '11px', color: '#999' }}>Wildcard - all actions</div>
                    </div>
                  </Option>
                </Select>
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit" icon={<SafetyOutlined />} loading={loading}>
                  Check Permission
                </Button>
              </Form.Item>
            </Form>

            {checkResult && (
              <Card
                style={{
                  marginTop: 16,
                  background: checkResult.allowed ? '#f6ffed' : '#fff1f0',
                  borderColor: checkResult.allowed ? '#b7eb8f' : '#ffa39e',
                }}
              >
                <Space direction="vertical" size="large" style={{ width: '100%' }}>
                  <div style={{ textAlign: 'center' }}>
                    {checkResult.allowed ? (
                      <CheckCircleOutlined style={{ fontSize: 48, color: '#52c41a' }} />
                    ) : (
                      <CloseCircleOutlined style={{ fontSize: 48, color: '#ff4d4f' }} />
                    )}
                  </div>
                  <Descriptions column={1} bordered>
                    <Descriptions.Item label="Result">
                      <Tag color={checkResult.allowed ? 'success' : 'error'} style={{ fontSize: '14px', padding: '4px 12px' }}>
                        {checkResult.allowed ? 'ALLOWED' : 'DENIED'}
                      </Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="Reason">
                      <div style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                        {checkResult.reason || 'No reason provided'}
                      </div>
                    </Descriptions.Item>
                  </Descriptions>
                  {!checkResult.allowed && (
                    <div style={{ marginTop: 16, padding: 12, background: '#fff', borderRadius: 4, border: '1px solid #ffccc7' }}>
                      <strong style={{ color: '#ff4d4f' }}>💡 Tip:</strong>
                      <div style={{ marginTop: 8, color: '#666' }}>
                        {checkResult.reason?.includes('no permissions assigned') ? (
                          <div>
                            Go to the <strong>"Assign Permission"</strong> tab and assign the required permission to this user.
                            Make sure to select a permission that matches the resource and action you're checking for.
                          </div>
                        ) : (
                          <div>
                            Make sure the user has been assigned a permission with the correct resource and action.
                            Check the user's current permissions in the "Assign Permission" tab.
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </Space>
              </Card>
            )}

            {selectedUserId && userPermissions.length > 0 && (
              <Card title="User's Current Permissions" style={{ marginTop: 16 }}>
                <Table
                  columns={permissionColumns}
                  dataSource={userPermissions.map((perm, index) => ({ key: index, permission: perm }))}
                  pagination={false}
                  size="small"
                />
              </Card>
            )}
          </Card>
      ),
    },
      {
      key: 'assign',
      label: 'Assign Permission',
      children: (
          <Card 
            title="Assign Permission to User"
            extra={
              <Button 
                type="primary" 
                icon={<PlusOutlined />} 
                onClick={() => setAssignModalVisible(true)}
              >
                Assign Permission
              </Button>
            }
          >
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <div>
                <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>Select User to View Permissions</label>
                <Select
                  showSearch
                  placeholder="Search and select a user to view their permissions"
                  optionFilterProp="label"
                  filterOption={false}
                  onSearch={handleUserSearch}
                  onChange={handleUserSelect}
                  loading={searchLoading}
                  style={{ width: '100%' }}
                  allowClear
                  value={selectedUserId}
                >
                  {userOptions.map(option => (
                    <Option key={option.key} value={option.value} label={option.label}>
                      {option.label}
                    </Option>
                  ))}
                </Select>
              </div>

              {selectedUserId && (
                <Card title="User's Assigned Permissions" style={{ marginTop: 16 }}>
                  {userPermissions.length > 0 ? (
                    <Table
                      columns={permissionColumns}
                      dataSource={userPermissions.map((perm, index) => ({ key: index, permission: perm }))}
                      pagination={false}
                      size="small"
                    />
                  ) : (
                    <p style={{ textAlign: 'center', color: '#999', padding: '20px 0' }}>
                      No permissions assigned to this user yet. Click "Assign Permission" to add permissions.
                    </p>
                  )}
                </Card>
              )}
            </Space>
          </Card>
      ),
    },
  ];

  return (
    <div>
      <h2>Permission Management</h2>
      
      <Tabs defaultActiveKey="check" items={tabItems} style={{ marginTop: 16 }} />

      <Modal
        title="Assign Permission to User"
        open={assignModalVisible}
        onCancel={() => {
          setAssignModalVisible(false);
          assignForm.resetFields();
        }}
        footer={null}
      >
        <Form form={assignForm} onFinish={handleAssignPermission} layout="vertical">
          <Form.Item 
            name="user_id" 
            label="User"
            tooltip="Select a user from the dropdown. You can type to search by username or email."
            rules={[
              { required: true, message: 'Please select a user' },
              {
                validator: (_, value) => {
                  if (!value) {
                    return Promise.resolve();
                  }
                  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
                  if (!uuidRegex.test(value)) {
                    return Promise.reject(new Error('Invalid user ID format. Please select from dropdown'));
                  }
                  return Promise.resolve();
                },
              },
            ]}
            extra={<span style={{ color: '#666', fontSize: '12px' }}>Select from dropdown - DO NOT type manually</span>}
          >
            <Select
              showSearch
              placeholder="Search and select a user"
              optionFilterProp="label"
              filterOption={false}
              onSearch={handleUserSearch}
              loading={searchLoading}
              style={{ width: '100%' }}
            >
              {userOptions.map(option => (
                <Option key={option.key} value={option.value} label={option.label}>
                  {option.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item 
            name="permission_id" 
            label="Permission"
            tooltip="Select the permission to assign to the user"
            rules={[{ required: true, message: 'Please select a permission' }]}
          >
            <Select
              placeholder="Select a permission"
              style={{ width: '100%' }}
              showSearch
              optionFilterProp="label"
            >
              {permissions.map(perm => (
                <Option key={perm.id} value={perm.id} label={`${perm.name} (${perm.resource}:${perm.action})`}>
                  <div>
                    <div><strong>{perm.name}</strong></div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      {perm.resource}:{perm.action}
                      {perm.description && ` - ${perm.description}`}
                    </div>
                  </div>
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" icon={<CheckOutlined />} loading={assignLoading}>
                Assign Permission
              </Button>
              <Button onClick={() => {
                setAssignModalVisible(false);
                assignForm.resetFields();
              }}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default PermissionManagement;
