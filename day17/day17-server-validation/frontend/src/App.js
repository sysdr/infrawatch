import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import Dashboard from './pages/Dashboard';
import ServerValidation from './pages/ServerValidation';
import NetworkDiscovery from './pages/NetworkDiscovery';
import HealthMonitoring from './pages/HealthMonitoring';
import Navigation from './components/Navigation';
import 'antd/dist/reset.css';
import './App.css';

const { Content } = Layout;

function App() {
  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Navigation />
        <Layout style={{ marginLeft: 200 }}>
          <Content style={{ margin: '24px 16px 0', overflow: 'initial' }}>
            <div style={{ padding: 24, background: '#fff', minHeight: 360 }}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/validation" element={<ServerValidation />} />
                <Route path="/discovery" element={<NetworkDiscovery />} />
                <Route path="/health" element={<HealthMonitoring />} />
              </Routes>
            </div>
          </Content>
        </Layout>
      </Layout>
    </Router>
  );
}

export default App;
