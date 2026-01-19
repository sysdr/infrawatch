import React, { useState } from 'react';
import { Layout, Menu } from 'antd';
import {
  DashboardOutlined,
  AlertOutlined,
  SettingOutlined,
  FileTextOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import SecurityDashboard from './components/dashboard/SecurityDashboard';
import SecurityEvents from './components/events/SecurityEvents';
import SecuritySettings from './components/settings/SecuritySettings';
import AuditLogs from './components/audit/AuditLogs';
import SecurityReports from './components/reports/SecurityReports';
import './App.css';

const { Header, Sider, Content } = Layout;

function App() {
  const [selectedMenu, setSelectedMenu] = useState('dashboard');

  const renderContent = () => {
    switch (selectedMenu) {
      case 'dashboard':
        return <SecurityDashboard />;
      case 'events':
        return <SecurityEvents />;
      case 'settings':
        return <SecuritySettings />;
      case 'audit':
        return <AuditLogs />;
      case 'reports':
        return <SecurityReports />;
      default:
        return <SecurityDashboard />;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={250} theme="light">
        <div style={{ 
          padding: '24px', 
          fontSize: '20px', 
          fontWeight: 'bold',
          borderBottom: '1px solid #f0f0f0'
        }}>
          Security Center
        </div>
        <Menu
          mode="inline"
          selectedKeys={[selectedMenu]}
          onClick={({ key }) => setSelectedMenu(key)}
          style={{ marginTop: '16px' }}
          items={[
            {
              key: 'dashboard',
              icon: <DashboardOutlined />,
              label: 'Dashboard',
            },
            {
              key: 'events',
              icon: <AlertOutlined />,
              label: 'Security Events',
            },
            {
              key: 'settings',
              icon: <SettingOutlined />,
              label: 'Settings',
            },
            {
              key: 'audit',
              icon: <FileTextOutlined />,
              label: 'Audit Logs',
            },
            {
              key: 'reports',
              icon: <BarChartOutlined />,
              label: 'Reports',
            },
          ]}
        />
      </Sider>
      <Layout>
        <Header style={{ 
          background: '#fff', 
          padding: '0 24px',
          borderBottom: '1px solid #f0f0f0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <h1 style={{ margin: 0, fontSize: '24px' }}>Security Monitoring & Management</h1>
          <div style={{ color: '#888' }}>
            Real-time Security Intelligence
          </div>
        </Header>
        <Content style={{ margin: '24px', background: '#f5f5f5' }}>
          {renderContent()}
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
