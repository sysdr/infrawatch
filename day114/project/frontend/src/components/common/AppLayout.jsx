import React, { useState } from 'react';
import { Layout, Menu, Typography, Badge, Tag } from 'antd';
import {
  DashboardOutlined, ThunderboltOutlined, AppstoreOutlined,
  CloudServerOutlined, MenuFoldOutlined, MenuUnfoldOutlined
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;

const navItems = [
  { key: '/dashboard', icon: <DashboardOutlined />, label: 'Overview' },
  { key: '/vitals',    icon: <ThunderboltOutlined />, label: 'Core Web Vitals' },
  { key: '/bundles',   icon: <AppstoreOutlined />, label: 'Bundle Analysis' },
  { key: '/sw',        icon: <CloudServerOutlined />, label: 'Service Worker' },
];

export default function AppLayout({ children }) {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const { pathname } = useLocation();

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme="light"
        width={220}
        style={{
          boxShadow: '2px 0 12px rgba(0,0,0,0.08)',
          background: '#fff',
          position: 'fixed', left: 0, top: 0, bottom: 0, zIndex: 100,
        }}
      >
        <div style={{
          padding: '20px 16px 16px',
          borderBottom: '1px solid #f0f0f0',
          background: 'linear-gradient(135deg, #1b4332, #2d6a4f)',
        }}>
          <Title level={4} style={{ color: '#fff', margin: 0, fontSize: collapsed ? 12 : 14 }}>
            {collapsed ? '⚡' : '⚡ PerfDash'}
          </Title>
          {!collapsed && (
            <Text style={{ color: '#95d5b2', fontSize: 11 }}>Day 114 · Frontend Performance</Text>
          )}
        </div>
        <Menu
          mode="inline"
          selectedKeys={[pathname]}
          items={navItems}
          onClick={({ key }) => navigate(key)}
          style={{ border: 'none', marginTop: 8 }}
        />
      </Sider>

      <Layout style={{ marginLeft: collapsed ? 80 : 220, transition: 'margin 0.2s' }}>
        <Header style={{
          background: '#fff', padding: '0 24px', display: 'flex',
          alignItems: 'center', justifyContent: 'space-between',
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)', position: 'sticky', top: 0, zIndex: 99
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            {React.createElement(collapsed ? MenuUnfoldOutlined : MenuFoldOutlined, {
              onClick: () => setCollapsed(!collapsed),
              style: { fontSize: 18, cursor: 'pointer', color: '#2d6a4f' }
            })}
            <Text strong style={{ color: '#1b4332' }}>Frontend Performance Monitoring</Text>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <Tag color="green">Live</Tag>
            <Tag color="blue">Day 114</Tag>
          </div>
        </Header>
        <Content style={{ padding: 24, minHeight: 'calc(100vh - 64px)' }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
}
