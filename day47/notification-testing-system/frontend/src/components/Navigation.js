import React from 'react';
import { Layout, Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import { DashboardOutlined, ExperimentOutlined, MonitorOutlined } from '@ant-design/icons';

const { Sider } = Layout;

const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/testing',
      icon: <ExperimentOutlined />,
      label: 'Testing',
    },
    {
      key: '/monitoring',
      icon: <MonitorOutlined />,
      label: 'Monitoring',
    },
  ];

  return (
    <Sider width={200} style={{ background: '#fff' }}>
      <div style={{ height: '32px', margin: '16px', background: 'rgba(255,255,255,.3)' }} />
      <Menu
        mode="inline"
        selectedKeys={[location.pathname]}
        style={{ height: '100%', borderRight: 0 }}
        items={menuItems}
        onClick={({ key }) => navigate(key)}
      />
    </Sider>
  );
};

export default Navigation;
