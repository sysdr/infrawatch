import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { ArrowLeft, Send, Eye } from 'lucide-react';
import axios from 'axios';

const Container = styled.div`
  max-width: 800px;
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

const Card = styled.div`
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
`;

const Form = styled.form`
  display: grid;
  gap: 1rem;
`;

const Input = styled.input`
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 1rem;
`;

const Select = styled.select`
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 1rem;
`;

const TextArea = styled.textarea`
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 1rem;
  resize: vertical;
  min-height: 100px;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
`;

const Button = styled.button`
  background: ${props => props.secondary ? '#718096' : '#667eea'};
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const ResultCard = styled.div`
  background: ${props => props.success ? '#f0fff4' : '#fed7d7'};
  border: 1px solid ${props => props.success ? '#9ae6b4' : '#feb2b2'};
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
`;

function NotificationTester() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [notification, setNotification] = useState({
    category: 'security',
    priority: 'high',
    title: 'Security Alert',
    message: 'Suspicious login attempt detected',
    data: {}
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const simulateNotification = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post('/api/v1/notifications/simulate', {
        user_id: parseInt(userId),
        ...notification
      });
      setResult({ type: 'simulation', data: response.data });
    } catch (error) {
      setResult({ type: 'error', data: error.response?.data || error.message });
    } finally {
      setLoading(false);
    }
  };

  const sendNotification = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/v1/notifications/send', {
        user_id: parseInt(userId),
        ...notification
      });
      setResult({ type: 'sent', data: response.data });
    } catch (error) {
      setResult({ type: 'error', data: error.response?.data || error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <BackButton onClick={() => navigate(`/preferences/${userId}`)}>
        <ArrowLeft size={20} />
        Back to Preferences
      </BackButton>

      <Card>
        <h2>Test Notification Preferences</h2>
        <p style={{ color: '#718096', margin: '0.5rem 0 1.5rem 0' }}>
          Test how your preferences affect different types of notifications
        </p>

        <Form onSubmit={simulateNotification}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Category
            </label>
            <Select
              value={notification.category}
              onChange={(e) => setNotification({ ...notification, category: e.target.value })}
            >
              <option value="security">Security</option>
              <option value="system">System</option>
              <option value="social">Social</option>
              <option value="marketing">Marketing</option>
              <option value="updates">Updates</option>
            </Select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Priority
            </label>
            <Select
              value={notification.priority}
              onChange={(e) => setNotification({ ...notification, priority: e.target.value })}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </Select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Title
            </label>
            <Input
              value={notification.title}
              onChange={(e) => setNotification({ ...notification, title: e.target.value })}
              placeholder="Notification title"
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Message
            </label>
            <TextArea
              value={notification.message}
              onChange={(e) => setNotification({ ...notification, message: e.target.value })}
              placeholder="Notification message content"
            />
          </div>

          <ButtonGroup>
            <Button type="submit" disabled={loading}>
              <Eye size={16} />
              {loading ? 'Testing...' : 'Simulate Processing'}
            </Button>
            <Button type="button" secondary onClick={sendNotification} disabled={loading}>
              <Send size={16} />
              Send Notification
            </Button>
          </ButtonGroup>
        </Form>

        {result && (
          <ResultCard success={result.type !== 'error'}>
            <h4 style={{ margin: '0 0 1rem 0' }}>
              {result.type === 'simulation' ? 'Simulation Result' : 
               result.type === 'sent' ? 'Notification Sent' : 'Error'}
            </h4>
            <pre style={{ 
              background: 'rgba(255, 255, 255, 0.5)', 
              padding: '1rem', 
              borderRadius: '4px',
              overflow: 'auto',
              fontSize: '0.9rem'
            }}>
              {JSON.stringify(result.data, null, 2)}
            </pre>
          </ResultCard>
        )}
      </Card>
    </Container>
  );
}

export default NotificationTester;
