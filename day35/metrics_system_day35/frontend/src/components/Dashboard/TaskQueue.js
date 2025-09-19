import React from 'react';
import styled from 'styled-components';
import { formatDistanceToNow } from 'date-fns';

const Container = styled.div`
  padding: 20px;
`;

const Title = styled.h3`
  color: #1d2327;
  font-size: 18px;
  margin-bottom: 15px;
  border-bottom: 1px solid #c3c4c7;
  padding-bottom: 10px;
`;

const TaskItem = styled.div`
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f1;
  display: flex;
  justify-content: between;
  align-items: center;
`;

const TaskInfo = styled.div`
  flex: 1;
`;

const TaskType = styled.div`
  font-weight: 500;
  color: #1d2327;
`;

const TaskStatus = styled.span`
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 500;
  background: ${props => {
    switch (props.status) {
      case 'success': return '#d1e7dd';
      case 'failed': return '#f8d7da';
      case 'processing': return '#fff3cd';
      default: return '#d1ecf1';
    }
  }};
  color: ${props => {
    switch (props.status) {
      case 'success': return '#0f5132';
      case 'failed': return '#842029';
      case 'processing': return '#664d03';
      default: return '#055160';
    }
  }};
`;

function TaskQueue({ tasks }) {
  if (!tasks || tasks.length === 0) {
    return (
      <Container>
        <Title>Recent Tasks</Title>
        <p>No tasks found</p>
      </Container>
    );
  }

  return (
    <Container>
      <Title>Recent Tasks</Title>
      {tasks.map(task => (
        <TaskItem key={task.id}>
          <TaskInfo>
            <TaskType>{task.task_type}</TaskType>
            <div style={{ fontSize: '12px', color: '#646970' }}>
              {formatDistanceToNow(new Date(task.created_at), { addSuffix: true })}
            </div>
          </TaskInfo>
          <TaskStatus status={task.status}>
            {task.status}
          </TaskStatus>
        </TaskItem>
      ))}
    </Container>
  );
}

export default TaskQueue;
