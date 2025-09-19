import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
`;

const Title = styled.h1`
  color: #1d2327;
  font-size: 23px;
  margin-bottom: 30px;
`;

function TaskMonitor() {
  return (
    <Container>
      <Title>Task Monitor</Title>
      <p>Task monitoring interface coming soon...</p>
    </Container>
  );
}

export default TaskMonitor;
