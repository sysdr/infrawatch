import React from 'react';
import { Layout, Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  SafetyCertificateOutlined,
  RadarChartOutlined,
  HeartOutlined
} from '@ant-design/icons';

const { Sider } = Layout;

function Navigation() {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/validation',
      icon: <SafetyCertificateOutlined />,
      label: 'Server Validation',
    },
    {
      key: '/discovery',
      icon: <RadarChartOutlined />,
      label: 'Network Discovery',
    },
    {
      key: '/health',
      icon: <HeartOutlined />,
      label: 'Health Monitoring',
    },
  ];

  return (
    <Sider
      style={{
        overflow: 'auto',
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
        background: '#001529'
      }}
    >
      <div style={{ 
        height: '32px', 
        margin: '16px', 
        background: 'rgba(255, 255, 255, 0.3)',
        borderRadius: '6px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontWeight: 'bold'
      }}>
        Server Health
      </div>
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={({ key }) => navigate(key)}
      />
    </Sider>
  );
}

export default Navigation;
