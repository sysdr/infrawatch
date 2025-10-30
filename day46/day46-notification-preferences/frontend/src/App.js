import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled from 'styled-components';
import PreferencesDashboard from './components/PreferencesDashboard';
import NotificationTester from './components/NotificationTester';
import UserSelector from './components/UserSelector';

const AppContainer = styled.div`
  min-height: 100vh;
  background: #f3f4f6; /* neutral light gray */
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
`;

const Header = styled.header`
  background: #ffffff;
  padding: 1rem 2rem;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.05);
`;

const Title = styled.h1`
  margin: 0;
  color: #111827; /* slate-900 */
  font-weight: 700;
  font-size: 1.8rem;
`;

const Subtitle = styled.p`
  margin: 0.5rem 0 0 0;
  color: #6b7280; /* gray-500 */
  font-size: 0.9rem;
`;

function App() {
  return (
    <AppContainer>
      <Router>
        <Header>
          <Title>🔔 Notification Preferences Dashboard</Title>
          <Subtitle>Day 46: Smart notification control with preferences, quiet hours & escalation rules</Subtitle>
        </Header>
        <Routes>
          <Route path="/" element={<UserSelector />} />
          <Route path="/preferences/:userId" element={<PreferencesDashboard />} />
          <Route path="/test/:userId" element={<NotificationTester />} />
        </Routes>
      </Router>
    </AppContainer>
  );
}

export default App;
