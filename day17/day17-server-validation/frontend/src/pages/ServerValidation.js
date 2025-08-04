import React, { useState } from 'react';
import { Card, Form, Input, InputNumber, Button, Alert, Descriptions, Tag, Spin, Row, Col } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, LoadingOutlined } from '@ant-design/icons';

function ServerValidation() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [validationResult, setValidationResult] = useState(null);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const response = await fetch('/api/validation/validate-server', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });
      
      const data = await response.json();
      setValidationResult(data.validation_results);
    } catch (error) {
      console.error('Validation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (isValid) => {
    return isValid ? (
      <CheckCircleOutlined style={{ color: 'green' }} />
    ) : (
      <CloseCircleOutlined style={{ color: 'red' }} />
    );
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'green';
      case 'degraded': return 'orange';
      case 'unhealthy': return 'red';
      case 'unreachable': return 'gray';
      default: return 'blue';
    }
  };

  return (
    <div>
      <h1>Server Validation</h1>
      
      <Row gutter={16}>
        <Col span={12}>
          <Card title="Validate Server">
            <Form
              form={form}
              layout="vertical"
              onFinish={onFinish}
              initialValues={{ port: 80 }}
            >
              <Form.Item
                label="Hostname"
                name="hostname"
                rules={[{ required: true, message: 'Please enter hostname' }]}
              >
                <Input placeholder="example.com" />
              </Form.Item>
              
              <Form.Item
                label="IP Address"
                name="ip_address"
                rules={[{ required: true, message: 'Please enter IP address' }]}
              >
                <Input placeholder="192.168.1.1" />
              </Form.Item>
              
              <Form.Item
                label="Port"
                name="port"
                rules={[{ required: true, message: 'Please enter port' }]}
              >
                <InputNumber min={1} max={65535} style={{ width: '100%' }} />
              </Form.Item>
              
              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  loading={loading}
                  style={{ width: '100%' }}
                >
                  Validate Server
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>
        
        <Col span={12}>
          <Card title="Validation Results">
            {loading && (
              <div style={{ textAlign: 'center', padding: '50px' }}>
                <Spin size="large" indicator={<LoadingOutlined />} />
                <div style={{ marginTop: 16 }}>Validating server...</div>
              </div>
            )}
            
            {!loading && !validationResult && (
              <div style={{ textAlign: 'center', padding: '50px', color: '#999' }}>
                Enter server details and click validate to see results
              </div>
            )}
            
            {!loading && validationResult && (
              <div>
                <Alert
                  message={`Overall Status: ${validationResult.overall_status.toUpperCase()}`}
                  type={validationResult.overall_status === 'healthy' ? 'success' : 
                        validationResult.overall_status === 'degraded' ? 'warning' : 'error'}
                  style={{ marginBottom: 16 }}
                />
                
                <Descriptions column={1} bordered>
                  <Descriptions.Item 
                    label="Hostname Validation"
                    span={3}
                  >
                    {getStatusIcon(validationResult.hostname_valid)}
                    <span style={{ marginLeft: 8 }}>
                      {validationResult.hostname_message}
                    </span>
                  </Descriptions.Item>
                  
                  <Descriptions.Item 
                    label="IP Address Validation"
                    span={3}
                  >
                    {getStatusIcon(validationResult.ip_valid)}
                    <span style={{ marginLeft: 8 }}>
                      {validationResult.ip_message}
                    </span>
                  </Descriptions.Item>
                  
                  <Descriptions.Item 
                    label="Connectivity"
                    span={3}
                  >
                    {getStatusIcon(validationResult.connectivity.reachable)}
                    <span style={{ marginLeft: 8 }}>
                      {validationResult.connectivity.reachable ? 
                        `Reachable (${Math.round(validationResult.connectivity.response_time)}ms)` :
                        validationResult.connectivity.error
                      }
                    </span>
                  </Descriptions.Item>
                  
                  {validationResult.health.status && (
                    <Descriptions.Item 
                      label="Health Status"
                      span={3}
                    >
                      <Tag color={getStatusColor(validationResult.health.status)}>
                        {validationResult.health.status.toUpperCase()}
                      </Tag>
                      {validationResult.health.response_time && (
                        <span style={{ marginLeft: 8 }}>
                          {Math.round(validationResult.health.response_time)}ms
                        </span>
                      )}
                    </Descriptions.Item>
                  )}
                  
                  {validationResult.ssl.valid !== undefined && (
                    <Descriptions.Item 
                      label="SSL Certificate"
                      span={3}
                    >
                      {getStatusIcon(validationResult.ssl.valid)}
                      <span style={{ marginLeft: 8 }}>
                        {validationResult.ssl.valid ? 
                          `Valid (expires in ${validationResult.ssl.days_until_expiry} days)` :
                          validationResult.ssl.error
                        }
                      </span>
                    </Descriptions.Item>
                  )}
                </Descriptions>
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default ServerValidation;
