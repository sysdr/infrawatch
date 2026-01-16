import React, { useState } from 'react';
import { Layout, Menu } from 'antd';
import { KeyOutlined, FileTextOutlined, LineChartOutlined, SafetyOutlined } from '@ant-design/icons';
import APIKeyManagement from './components/APIKeyManagement';
import RequestLogs from './components/RequestLogs';
import Analytics from './components/Analytics';
import SecuritySettings from './components/SecuritySettings';

const { Header, Sider, Content } = Layout;

function App() {
  const [selectedMenu, setSelectedMenu] = useState('keys');

  const menuItems = [
    { key: 'keys', icon: <KeyOutlined />, label: 'API Keys' },
    { key: 'logs', icon: <FileTextOutlined />, label: 'Request Logs' },
    { key: 'analytics', icon: <LineChartOutlined />, label: 'Analytics' },
    { key: 'security', icon: <SafetyOutlined />, label: 'Security' }
  ];

  const renderContent = () => {
    switch (selectedMenu) {
      case 'keys':
        return <APIKeyManagement />;
      case 'logs':
        return <RequestLogs />;
      case 'analytics':
        return <Analytics />;
      case 'security':
        return <SecuritySettings />;
      default:
        return <APIKeyManagement />;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ 
        display: 'flex', 
        alignItems: 'center', 
        background: '#001529',
        padding: '0 24px'
      }}>
        <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
          🔐 API Security Dashboard
        </div>
      </Header>
      <Layout>
        <Sider width={200} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            selectedKeys={[selectedMenu]}
            onClick={({ key }) => setSelectedMenu(key)}
            items={menuItems}
            style={{ height: '100%', borderRight: 0 }}
          />
        </Sider>
        <Layout style={{ padding: '24px' }}>
          <Content
            style={{
              padding: 24,
              margin: 0,
              minHeight: 280,
              background: '#fff',
              borderRadius: '8px'
            }}
          >
            {renderContent()}
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
}

export default App;
