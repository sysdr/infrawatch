import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import Dashboard from './components/dashboard/Dashboard';
import MetricsChart from './components/charts/MetricsChart';
import AgentStatus from './components/agents/AgentStatus';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
`;

const Header = styled.div`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 1rem 2rem;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
`;

const Title = styled.h1`
  margin: 0;
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const StatusIndicator = styled.div`
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: ${props => props.connected ? '#27ae60' : '#e74c3c'};
  box-shadow: 0 0 0 3px ${props => props.connected ? 'rgba(39, 174, 96, 0.3)' : 'rgba(231, 76, 60, 0.3)'};
`;

const MainContent = styled.div`
  padding: 2rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
`;

const Card = styled.div`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  }
`;

function App() {
  const [connected, setConnected] = useState(false);
  const [stats, setStats] = useState({});
  const [recentMetrics, setRecentMetrics] = useState([]);

  useEffect(() => {
    // Native WebSocket connection for real-time updates
    const ws = new WebSocket('ws://localhost:8000/ws/dashboard');
    
    ws.onopen = () => {
      setConnected(true);
      console.log('Connected to metrics engine');
    };

    ws.onclose = () => {
      setConnected(false);
      console.log('Disconnected from metrics engine');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'stats_update') {
          setStats(data.data || {});
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    // Fetch recent metrics periodically
    const fetchMetrics = async () => {
      try {
        const response = await fetch('/api/v1/metrics/recent?limit=50');
        const data = await response.json();
        setRecentMetrics(data);
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      }
    };

    fetchMetrics();
    const metricsInterval = setInterval(fetchMetrics, 5000);

    return () => {
      ws.close();
      clearInterval(metricsInterval);
    };
  }, []);

  return (
    <AppContainer>
      <Header>
        <Title>
          <StatusIndicator connected={connected} />
          Metrics Collection Engine
          <span style={{fontSize: '0.6em', color: '#7f8c8d'}}>v1.0</span>
        </Title>
      </Header>
      
      <MainContent>
        <Card style={{gridColumn: 'span 2'}}>
          <Dashboard stats={stats} connected={connected} />
        </Card>
        
        <Card>
          <MetricsChart metrics={recentMetrics} />
        </Card>
        
        <Card>
          <AgentStatus stats={stats} />
        </Card>
      </MainContent>
    </AppContainer>
  );
}

export default App;
