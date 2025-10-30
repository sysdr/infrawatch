import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { ArrowLeft, Bell, Clock, Zap, Settings } from 'lucide-react';
import axios from 'axios';
import ChannelPreferences from './ChannelPreferences';
import QuietHours from './QuietHours';
import EscalationRules from './EscalationRules';

const Container = styled.div`
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1rem;
`;

const BackButton = styled.button`
  background: rgba(255, 255, 255, 0.9);
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-weight: 500;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
`;

const Dashboard = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled.div`
  background: #ffffff;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
`;

const CardHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
`;

const CardTitle = styled.h3`
  margin: 0;
  color: #111827;
  font-weight: 600;
`;

const TestButton = styled.button`
  background: #4f46e5; /* indigo-600 */
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 2rem auto 0;
  transition: background 0.2s;
  
  &:hover {
    background: #4338ca; /* indigo-700 */
  }
`;

function PreferencesDashboard() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [preferences, setPreferences] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserData();
  }, [userId]);

  const fetchUserData = async () => {
    try {
      const [userResponse, prefResponse] = await Promise.all([
        axios.get(`/api/v1/users/${userId}`),
        axios.get(`/api/v1/preferences/${userId}`)
      ]);
      
      setUser(userResponse.data);
      setPreferences(prefResponse.data);
    } catch (error) {
      console.error('Error fetching user data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Container>Loading...</Container>;
  }

  return (
    <Container>
      <BackButton onClick={() => navigate('/')}>
        <ArrowLeft size={20} />
        Back to Users
      </BackButton>
      
      <Card style={{ marginBottom: '2rem' }}>
        <h2>Notification Preferences for {user?.username}</h2>
        <p style={{ color: '#718096', margin: '0.5rem 0 0 0' }}>
          Configure how and when you receive notifications
        </p>
      </Card>

      <Dashboard>
        <Card>
          <CardHeader>
            <Bell size={24} color="#4f46e5" />
            <CardTitle>Channel Preferences</CardTitle>
          </CardHeader>
          <ChannelPreferences userId={userId} preferences={preferences} onUpdate={fetchUserData} />
        </Card>

        <Card>
          <CardHeader>
            <Clock size={24} color="#4f46e5" />
            <CardTitle>Quiet Hours</CardTitle>
          </CardHeader>
          <QuietHours userId={userId} preferences={preferences} onUpdate={fetchUserData} />
        </Card>

        <Card style={{ gridColumn: '1 / -1' }}>
          <CardHeader>
            <Zap size={24} color="#4f46e5" />
            <CardTitle>Escalation Rules</CardTitle>
          </CardHeader>
          <EscalationRules userId={userId} preferences={preferences} onUpdate={fetchUserData} />
        </Card>
      </Dashboard>

      <TestButton onClick={() => navigate(`/test/${userId}`)}>
        <Settings size={20} />
        Test Notification Preferences
      </TestButton>
    </Container>
  );
}

export default PreferencesDashboard;
