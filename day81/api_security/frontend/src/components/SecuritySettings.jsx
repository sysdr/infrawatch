import React from 'react';
import { Card, Descriptions, Tag, Space, Alert, Divider } from 'antd';
import { SafetyOutlined, LockOutlined, ClockCircleOutlined, GlobalOutlined, AuditOutlined } from '@ant-design/icons';

function SecuritySettings() {
  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>Security Configuration</h2>

      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Alert
          message="Security Status: Active"
          description="All security mechanisms are enabled and functioning correctly."
          type="success"
          showIcon
          icon={<SafetyOutlined />}
        />

        <Card title={<><LockOutlined /> Rate Limiting</>}>
          <Descriptions bordered column={2}>
            <Descriptions.Item label="Algorithm">Token Bucket</Descriptions.Item>
            <Descriptions.Item label="Storage">Redis (Distributed)</Descriptions.Item>
            <Descriptions.Item label="Default Limit">100 requests/minute</Descriptions.Item>
            <Descriptions.Item label="Burst Allowance">Configurable per key</Descriptions.Item>
            <Descriptions.Item label="Response Headers">
              <Space size={[0, 4]} wrap>
                <Tag>X-RateLimit-Limit</Tag>
                <Tag>X-RateLimit-Remaining</Tag>
                <Tag>X-RateLimit-Reset</Tag>
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="Error Code">429 Too Many Requests</Descriptions.Item>
          </Descriptions>
        </Card>

        <Card title={<><AuditOutlined /> Request Signing</>}>
          <Descriptions bordered column={2}>
            <Descriptions.Item label="Algorithm">HMAC-SHA256</Descriptions.Item>
            <Descriptions.Item label="Signature Header">X-Signature</Descriptions.Item>
            <Descriptions.Item label="Timestamp Header">X-Timestamp</Descriptions.Item>
            <Descriptions.Item label="Max Age">5 minutes (300 seconds)</Descriptions.Item>
            <Descriptions.Item label="Replay Protection">
              <Tag color="green">Enabled</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Timing Attack Protection">
              <Tag color="green">Constant-time Comparison</Tag>
            </Descriptions.Item>
          </Descriptions>
          
          <Divider />
          
          <div>
            <strong>Signature Format:</strong>
            <pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 4, marginTop: 8 }}>
{`HMAC-SHA256(
  secret_key,
  timestamp + method + path + body
)`}
            </pre>
          </div>
        </Card>

        <Card title={<><GlobalOutlined /> IP Whitelisting</>}>
          <Descriptions bordered column={2}>
            <Descriptions.Item label="Notation">CIDR (Classless Inter-Domain Routing)</Descriptions.Item>
            <Descriptions.Item label="Validation">Pre-request Check</Descriptions.Item>
            <Descriptions.Item label="Default Behavior">
              <Tag color="blue">Allow All (if no whitelist)</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Error Code">403 Forbidden</Descriptions.Item>
            <Descriptions.Item label="Examples" span={2}>
              <Space size={[0, 4]} wrap>
                <Tag>192.168.1.0/24</Tag>
                <Tag>10.0.0.0/8</Tag>
                <Tag>172.16.0.0/12</Tag>
              </Space>
            </Descriptions.Item>
          </Descriptions>
        </Card>

        <Card title={<><SafetyOutlined /> Security Headers</>}>
          <Descriptions bordered column={1}>
            <Descriptions.Item label="Strict-Transport-Security">
              <code>max-age=31536000; includeSubDomains</code>
              <div style={{ marginTop: 4, color: '#666' }}>Forces HTTPS for 1 year</div>
            </Descriptions.Item>
            <Descriptions.Item label="X-Content-Type-Options">
              <code>nosniff</code>
              <div style={{ marginTop: 4, color: '#666' }}>Prevents MIME type sniffing</div>
            </Descriptions.Item>
            <Descriptions.Item label="X-Frame-Options">
              <code>DENY</code>
              <div style={{ marginTop: 4, color: '#666' }}>Prevents clickjacking attacks</div>
            </Descriptions.Item>
            <Descriptions.Item label="Content-Security-Policy">
              <code>default-src 'self'</code>
              <div style={{ marginTop: 4, color: '#666' }}>Mitigates XSS attacks</div>
            </Descriptions.Item>
            <Descriptions.Item label="X-API-Version">
              <code>v1.2025.05</code>
              <div style={{ marginTop: 4, color: '#666' }}>Tracks API version for compatibility</div>
            </Descriptions.Item>
          </Descriptions>
        </Card>

        <Card title={<><ClockCircleOutlined /> API Key Lifecycle</>}>
          <Descriptions bordered column={2}>
            <Descriptions.Item label="Generation">Cryptographically Secure (secrets module)</Descriptions.Item>
            <Descriptions.Item label="Storage">bcrypt hashed (cost factor 12)</Descriptions.Item>
            <Descriptions.Item label="Default Expiry">90 days</Descriptions.Item>
            <Descriptions.Item label="Rotation Grace Period">24 hours</Descriptions.Item>
            <Descriptions.Item label="Revocation">Immediate</Descriptions.Item>
            <Descriptions.Item label="Format">
              <code>prefix_keyid_secret</code>
            </Descriptions.Item>
          </Descriptions>
        </Card>

        <Alert
          message="Security Best Practices"
          description={
            <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
              <li>Rotate API keys every 90 days or upon suspected compromise</li>
              <li>Use IP whitelisting for internal/trusted services</li>
              <li>Monitor rate limit breaches for potential attacks</li>
              <li>Implement request signing for high-security endpoints</li>
              <li>Review request logs regularly for anomalies</li>
            </ul>
          }
          type="info"
          showIcon
        />
      </Space>
    </div>
  );
}

export default SecuritySettings;
