import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Form, 
  Input, 
  Switch, 
  Button, 
  Space, 
  Divider, 
  Typography,
  message,
  Tabs
} from 'antd';
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons';
import { securityApi } from '../../services/api';

const { Title, Text } = Typography;
const { TextArea } = Input;

function SecuritySettings() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [settings, setSettings] = useState([]);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await securityApi.getSettings();
      setSettings(response.data);
      
      // Initialize form with existing settings
      const formValues = {};
      response.data.forEach(setting => {
        formValues[setting.setting_key] = setting.setting_value;
      });
      form.setFieldsValue(formValues);
    } catch (error) {
      console.error('Error loading settings:', error);
      message.error('Failed to load settings');
    }
  };

  const handleSave = async (category) => {
    setLoading(true);
    try {
      const values = form.getFieldsValue();
      
      // Save each setting
      for (const [key, value] of Object.entries(values)) {
        const setting = settings.find(s => s.setting_key === key);
        if (setting) {
          await securityApi.updateSetting(key, {
            setting_value: value,
            modified_by: 'admin_user'
          });
        }
      }
      
      message.success('Settings saved successfully');
      setLoading(false);
    } catch (error) {
      console.error('Error saving settings:', error);
      message.error('Failed to save settings');
      setLoading(false);
    }
  };

  const authenticationSettings = (
    <Card>
      <Title level={4}>Authentication Settings</Title>
      <Form form={form} layout="vertical">
        <Form.Item
          label="Require Multi-Factor Authentication"
          name="mfa_required"
          valuePropName="checked"
        >
          <Switch />
        </Form.Item>
        
        <Form.Item
          label="Session Timeout (minutes)"
          name="session_timeout"
        >
          <Input type="number" placeholder="30" />
        </Form.Item>

        <Form.Item
          label="Maximum Login Attempts"
          name="max_login_attempts"
        >
          <Input type="number" placeholder="5" />
        </Form.Item>

        <Form.Item
          label="Password Minimum Length"
          name="password_min_length"
        >
          <Input type="number" placeholder="12" />
        </Form.Item>

        <Button 
          type="primary" 
          icon={<SaveOutlined />}
          onClick={() => handleSave('authentication')}
          loading={loading}
        >
          Save Authentication Settings
        </Button>
      </Form>
    </Card>
  );

  const threatDetectionSettings = (
    <Card>
      <Title level={4}>Threat Detection Settings</Title>
      <Form form={form} layout="vertical">
        <Form.Item
          label="Enable Automatic Blocking"
          name="auto_blocking_enabled"
          valuePropName="checked"
        >
          <Switch />
        </Form.Item>

        <Form.Item
          label="Threat Score Threshold"
          name="threat_score_threshold"
          tooltip="Events above this score trigger alerts"
        >
          <Input type="number" placeholder="70" />
        </Form.Item>

        <Form.Item
          label="Rate Limit (requests per minute)"
          name="rate_limit"
        >
          <Input type="number" placeholder="100" />
        </Form.Item>

        <Form.Item
          label="IP Whitelist"
          name="ip_whitelist"
          tooltip="Comma-separated IP addresses"
        >
          <TextArea rows={3} placeholder="192.168.1.1, 10.0.0.1" />
        </Form.Item>

        <Form.Item
          label="IP Blacklist"
          name="ip_blacklist"
          tooltip="Comma-separated IP addresses"
        >
          <TextArea rows={3} placeholder="203.0.113.0, 198.51.100.0" />
        </Form.Item>

        <Button 
          type="primary" 
          icon={<SaveOutlined />}
          onClick={() => handleSave('threat_detection')}
          loading={loading}
        >
          Save Threat Detection Settings
        </Button>
      </Form>
    </Card>
  );

  const notificationSettings = (
    <Card>
      <Title level={4}>Notification Settings</Title>
      <Form form={form} layout="vertical">
        <Form.Item
          label="Email Notifications"
          name="email_notifications_enabled"
          valuePropName="checked"
        >
          <Switch />
        </Form.Item>

        <Form.Item
          label="Notification Email"
          name="notification_email"
        >
          <Input type="email" placeholder="security@company.com" />
        </Form.Item>

        <Form.Item
          label="Notify on Critical Events"
          name="notify_critical"
          valuePropName="checked"
        >
          <Switch defaultChecked />
        </Form.Item>

        <Form.Item
          label="Notify on High Severity Events"
          name="notify_high"
          valuePropName="checked"
        >
          <Switch defaultChecked />
        </Form.Item>

        <Form.Item
          label="Daily Summary Report"
          name="daily_summary_enabled"
          valuePropName="checked"
        >
          <Switch />
        </Form.Item>

        <Button 
          type="primary" 
          icon={<SaveOutlined />}
          onClick={() => handleSave('notifications')}
          loading={loading}
        >
          Save Notification Settings
        </Button>
      </Form>
    </Card>
  );

  const complianceSettings = (
    <Card>
      <Title level={4}>Compliance Settings</Title>
      <Form form={form} layout="vertical">
        <Form.Item
          label="Enable Audit Logging"
          name="audit_logging_enabled"
          valuePropName="checked"
        >
          <Switch defaultChecked />
        </Form.Item>

        <Form.Item
          label="Log Retention Period (days)"
          name="log_retention_days"
        >
          <Input type="number" placeholder="365" />
        </Form.Item>

        <Form.Item
          label="GDPR Compliance Mode"
          name="gdpr_compliance_enabled"
          valuePropName="checked"
        >
          <Switch />
        </Form.Item>

        <Form.Item
          label="Data Encryption"
          name="data_encryption_enabled"
          valuePropName="checked"
        >
          <Switch defaultChecked />
        </Form.Item>

        <Button 
          type="primary" 
          icon={<SaveOutlined />}
          onClick={() => handleSave('compliance')}
          loading={loading}
        >
          Save Compliance Settings
        </Button>
      </Form>
    </Card>
  );

  const tabItems = [
    {
      key: 'authentication',
      label: 'Authentication',
      children: authenticationSettings,
    },
    {
      key: 'threat_detection',
      label: 'Threat Detection',
      children: threatDetectionSettings,
    },
    {
      key: 'notifications',
      label: 'Notifications',
      children: notificationSettings,
    },
    {
      key: 'compliance',
      label: 'Compliance',
      children: complianceSettings,
    },
  ];

  return (
    <div>
      <Card 
        title="Security Configuration"
        extra={
          <Button icon={<ReloadOutlined />} onClick={loadSettings}>
            Reload
          </Button>
        }
      >
        <Tabs items={tabItems} />
      </Card>
    </div>
  );
}

export default SecuritySettings;
