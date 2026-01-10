import React, { useMemo } from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import { UserOutlined, TeamOutlined, SafetyOutlined, BarChartOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import UserManagement from './components/UserManagement';
import TeamManagement from './components/TeamManagement';
import PermissionManagement from './components/PermissionManagement';
import ActivityDashboard from './components/ActivityDashboard';
import './App.css';

const { Header, Sider, Content } = Layout;

function AppContent() {
  const navigate = useNavigate();
  const location = useLocation();

  // Use useMemo to prevent unnecessary re-renders and ensure items structure is correct
  // Using proper MenuProps type ensures compatibility with Ant Design v5 items API
  const menuItems: MenuProps['items'] = useMemo(() => [
    {
      key: 'users',
      icon: <UserOutlined />,
      label: 'Users',
    },
    {
      key: 'teams',
      icon: <TeamOutlined />,
      label: 'Teams',
    },
    {
      key: 'permissions',
      icon: <SafetyOutlined />,
      label: 'Permissions',
    },
    {
      key: 'activity',
      icon: <BarChartOutlined />,
      label: 'Activity',
    },
  ], []);

  // Get selected key based on current route - memoized for performance
  const selectedKeys = useMemo(() => {
    const path = location.pathname;
    if (path === '/' || path === '/users') return ['users'];
    if (path === '/teams') return ['teams'];
    if (path === '/permissions') return ['permissions'];
    if (path === '/activity') return ['activity'];
    return ['users'];
  }, [location.pathname]);

  // Handle menu item click - using proper type from MenuProps
  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    switch (key) {
      case 'users':
        navigate('/');
        break;
      case 'teams':
        navigate('/teams');
        break;
      case 'permissions':
        navigate('/permissions');
        break;
      case 'activity':
        navigate('/activity');
        break;
      default:
        navigate('/');
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', background: '#001529' }}>
        <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold', marginRight: '50px' }}>
          User Management System
        </div>
      </Header>
      <Layout>
        <Sider width={200} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            selectedKeys={selectedKeys}
            items={menuItems}
            onClick={handleMenuClick}
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
              borderRadius: '8px',
            }}
          >
            <Routes>
              <Route path="/" element={<UserManagement />} />
              <Route path="/teams" element={<TeamManagement />} />
              <Route path="/permissions" element={<PermissionManagement />} />
              <Route path="/activity" element={<ActivityDashboard />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
}

function App() {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
