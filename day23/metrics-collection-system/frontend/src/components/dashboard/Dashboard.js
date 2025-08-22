import React from 'react';
import styled from 'styled-components';

const DashboardContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
`;

const StatCard = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
`;

const StatValue = styled.div`
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
`;

const StatLabel = styled.div`
  font-size: 0.9rem;
  opacity: 0.9;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const ConnectionStatus = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-weight: 600;
  color: ${props => props.connected ? '#27ae60' : '#e74c3c'};
`;

const Dashboard = ({ stats, connected }) => {
  return (
    <div>
      <h2 style={{marginTop: 0, color: '#2c3e50'}}>System Overview</h2>
      
      <ConnectionStatus connected={connected}>
        <div style={{
          width: '8px', 
          height: '8px', 
          borderRadius: '50%', 
          backgroundColor: connected ? '#27ae60' : '#e74c3c'
        }} />
        {connected ? 'Connected' : 'Disconnected'}
      </ConnectionStatus>

      <DashboardContainer>
        <StatCard>
          <StatValue>{stats.total_metrics || 0}</StatValue>
          <StatLabel>Total Metrics</StatLabel>
        </StatCard>
        
        <StatCard>
          <StatValue>{stats.metrics_per_second || 0}</StatValue>
          <StatLabel>Metrics/Second</StatLabel>
        </StatCard>
        
        <StatCard>
          <StatValue>{stats.active_agents || 0}</StatValue>
          <StatLabel>Active Agents</StatLabel>
        </StatCard>
        
        <StatCard>
          <StatValue>{stats.buffer_size || 0}</StatValue>
          <StatLabel>Buffer Size</StatLabel>
        </StatCard>
      </DashboardContainer>
    </div>
  );
};

export default Dashboard;
