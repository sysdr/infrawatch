import React from 'react';
import styled from 'styled-components';

const StatsContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const StatCard = styled.div`
  background: #fff;
  border: 1px solid #c3c4c7;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 1px 1px rgba(0,0,0,.04);
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 32px;
  font-weight: 600;
  color: ${props => props.color || '#2271b1'};
  margin-bottom: 5px;
`;

const StatLabel = styled.div`
  font-size: 14px;
  color: #646970;
  text-transform: uppercase;
  font-weight: 500;
`;

const StatSubtext = styled.div`
  font-size: 12px;
  color: #646970;
  margin-top: 5px;
`;

function StatsCards({ stats }) {
  if (!stats) return null;

  const cards = [
    {
      label: 'Total Tasks',
      value: stats.total_tasks,
      color: '#2271b1',
      subtext: `${stats.tasks_per_hour} created this hour`
    },
    {
      label: 'Processing',
      value: stats.processing_tasks,
      color: '#d63638',
      subtext: 'Currently running'
    },
    {
      label: 'Success Rate',
      value: `${stats.success_rate}%`,
      color: '#00a32a',
      subtext: 'Last 24 hours'
    },
    {
      label: 'Avg Duration',
      value: `${stats.avg_execution_time}s`,
      color: '#996f00',
      subtext: 'Execution time'
    },
    {
      label: 'Pending',
      value: stats.pending_tasks,
      color: '#996f00',
      subtext: 'In queue'
    },
    {
      label: 'Failed',
      value: stats.failed_tasks,
      color: '#d63638',
      subtext: 'Need attention'
    }
  ];

  return (
    <StatsContainer>
      {cards.map((card, index) => (
        <StatCard key={index}>
          <StatValue color={card.color}>{card.value}</StatValue>
          <StatLabel>{card.label}</StatLabel>
          <StatSubtext>{card.subtext}</StatSubtext>
        </StatCard>
      ))}
    </StatsContainer>
  );
}

export default StatsCards;
