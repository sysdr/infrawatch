import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

const AgentContainer = styled.div`
  max-height: 300px;
  overflow-y: auto;
`;

const AgentCard = styled.div`
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
`;

const AgentHeader = styled.div`
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 0.5rem;
`;

const AgentId = styled.div`
  font-weight: 600;
  font-size: 1.1rem;
`;

const AgentStats = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  font-size: 0.9rem;
  opacity: 0.9;
`;

const NoAgents = styled.div`
  text-align: center;
  color: #7f8c8d;
  padding: 2rem;
  font-style: italic;
`;

const SectionTitle = styled.h3`
  margin-top: 0;
  color: #2c3e50;
  margin-bottom: 1rem;
`;

const AgentStatus = ({ stats }) => {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const response = await fetch('/api/v1/agents');
        const data = await response.json();
        setAgents(Object.entries(data.agents || {}));
      } catch (error) {
        console.error('Failed to fetch agents:', error);
      }
    };

    fetchAgents();
    const interval = setInterval(fetchAgents, 5000);
    return () => clearInterval(interval);
  }, []);

  const formatUptime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${Math.floor(seconds % 60)}s`;
    } else {
      return `${Math.floor(seconds)}s`;
    }
  };

  return (
    <div>
      <SectionTitle>Connected Agents ({agents.length})</SectionTitle>
      
      <AgentContainer>
        {agents.length === 0 ? (
          <NoAgents>No agents connected</NoAgents>
        ) : (
          agents.map(([agentId, agentData]) => (
            <AgentCard key={agentId}>
              <AgentHeader>
                <AgentId>{agentId}</AgentId>
              </AgentHeader>
              <AgentStats>
                <div>Metrics Sent: {agentData.metrics_sent}</div>
                <div>Uptime: {formatUptime(agentData.uptime)}</div>
              </AgentStats>
            </AgentCard>
          ))
        )}
      </AgentContainer>
    </div>
  );
};

export default AgentStatus;
