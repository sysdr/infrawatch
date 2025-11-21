import React, { useState, useEffect, useRef } from 'react';
import { Card, Button, Input, Space, Tag, Divider, Statistic, Row, Col } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import pako from 'pako';

function ConnectionTest() {
  const [userId, setUserId] = useState('test_user_' + Math.random().toString(36).substr(2, 9));
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [stats, setStats] = useState({ received: 0, batches: 0 });
  const ws = useRef(null);

  const connect = () => {
    const websocket = new WebSocket(`ws://localhost:8000/ws/notifications/${userId}`);
    
    websocket.onopen = () => {
      setConnected(true);
      console.log('WebSocket connected');
    };

    websocket.onmessage = (event) => {
      if (event.data instanceof Blob) {
        const reader = new FileReader();
        reader.onload = () => {
          try {
            // Decompress
            const compressed = new Uint8Array(reader.result);
            const decompressed = pako.inflate(compressed, { to: 'string' });
            const batch = JSON.parse(decompressed);
            
            setStats(prev => ({
              received: prev.received + batch.count,
              batches: prev.batches + 1
            }));
            
            setMessages(prev => [...batch.notifications, ...prev].slice(0, 10));
          } catch (error) {
            console.error('Error processing message:', error);
          }
        };
        reader.readAsArrayBuffer(event.data);
      }
    };

    websocket.onclose = () => {
      setConnected(false);
      console.log('WebSocket disconnected');
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.current = websocket;
  };

  const disconnect = () => {
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
  };

  useEffect(() => {
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  const sendTestNotification = async () => {
    try {
      await fetch('http://localhost:8000/api/notifications/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          message: `Test notification at ${new Date().toLocaleTimeString()}`,
          priority: 'normal',
          notification_type: 'info'
        })
      });
    } catch (error) {
      console.error('Error sending notification:', error);
    }
  };

  const sendBulkNotifications = async () => {
    const notifications = Array.from({ length: 100 }, (_, i) => ({
      user_id: userId,
      message: `Bulk notification ${i + 1}`,
      priority: i % 10 === 0 ? 'critical' : 'normal',
      notification_type: 'info'
    }));

    try {
      await fetch('http://localhost:8000/api/notifications/bulk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(notifications)
      });
    } catch (error) {
      console.error('Error sending bulk notifications:', error);
    }
  };

  return (
    <Card title="WebSocket Connection Test">
      <Space direction="vertical" style={{ width: '100%' }}>
        <Input 
          value={userId} 
          onChange={(e) => setUserId(e.target.value)}
          placeholder="User ID"
          disabled={connected}
        />
        
        <Space>
          {!connected ? (
            <Button type="primary" onClick={connect}>Connect</Button>
          ) : (
            <Button danger onClick={disconnect}>Disconnect</Button>
          )}
          <Tag color={connected ? 'green' : 'red'}>
            {connected ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
            {connected ? 'Connected' : 'Disconnected'}
          </Tag>
        </Space>

        <Row gutter={16}>
          <Col span={12}>
            <Statistic title="Messages Received" value={stats.received} />
          </Col>
          <Col span={12}>
            <Statistic title="Batches Received" value={stats.batches} />
          </Col>
        </Row>

        <Divider />

        <Space>
          <Button onClick={sendTestNotification} disabled={!connected}>
            Send Test Message
          </Button>
          <Button onClick={sendBulkNotifications} disabled={!connected}>
            Send 100 Messages
          </Button>
        </Space>

        <Divider>Recent Messages</Divider>

        <div style={{ maxHeight: '200px', overflow: 'auto' }}>
          {messages.map((msg, idx) => (
            <div key={idx} style={{ 
              padding: '8px', 
              marginBottom: '4px', 
              background: '#f0f0f0',
              borderRadius: '4px',
              fontSize: '12px'
            }}>
              <Tag color={msg.priority === 'critical' ? 'red' : 'blue'}>
                {msg.priority}
              </Tag>
              {msg.message}
            </div>
          ))}
        </div>
      </Space>
    </Card>
  );
}

export default ConnectionTest;
