import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useQuery } from 'react-query';
import StatsCards from './StatsCards';
import TaskQueue from './TaskQueue';
import MetricsChart from './MetricsChart';
import CreateTaskModal from './CreateTaskModal';
import { fetchStats, fetchTasks } from '../../utils/api';

const DashboardContainer = styled.div`
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 30px;
  background: #fff;
  padding: 20px;
  border: 1px solid #c3c4c7;
  border-radius: 4px;
  box-shadow: 0 1px 1px rgba(0,0,0,.04);
`;

const Title = styled.h1`
  color: #1d2327;
  font-size: 23px;
  font-weight: 400;
  margin: 0;
`;

const CreateButton = styled.button`
  background: #2271b1;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 14px;
  
  &:hover {
    background: #135e96;
  }
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const Section = styled.div`
  background: #fff;
  border: 1px solid #c3c4c7;
  border-radius: 4px;
  box-shadow: 0 1px 1px rgba(0,0,0,.04);
`;

function Dashboard() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [wsData, setWsData] = useState(null);

  // Fetch initial data
  const { data: stats, refetch: refetchStats } = useQuery('stats', fetchStats, {
    refetchInterval: 5000,
  });

  const { data: tasks, refetch: refetchTasks } = useQuery('tasks', () => fetchTasks({ limit: 10 }), {
    refetchInterval: 3000,
  });

  // WebSocket connection for real-time updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'stats_update') {
        setWsData(data.data);
      }
    };

    return () => ws.close();
  }, []);

  const currentStats = wsData || stats;

  return (
    <DashboardContainer>
      <Header>
        <Title>Background Processing Dashboard</Title>
        <CreateButton onClick={() => setShowCreateModal(true)}>
          Create Task
        </CreateButton>
      </Header>

      {currentStats && <StatsCards stats={currentStats} />}

      <Grid>
        <Section>
          <MetricsChart />
        </Section>
        <Section>
          <TaskQueue tasks={tasks || []} />
        </Section>
      </Grid>

      {showCreateModal && (
        <CreateTaskModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            refetchStats();
            refetchTasks();
          }}
        />
      )}
    </DashboardContainer>
  );
}

export default Dashboard;
