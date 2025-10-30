import React, { useState } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const TimeInputs = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
`;

const Input = styled.input`
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
`;

const DaysSelector = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
`;

const DayButton = styled.button`
  padding: 0.5rem 1rem;
  border: 2px solid ${props => props.selected ? '#667eea' : '#e2e8f0'};
  background: ${props => props.selected ? '#667eea' : 'white'};
  color: ${props => props.selected ? 'white' : '#4a5568'};
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
`;

const ExceptionsList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
`;

const ExceptionTag = styled.span`
  background: #fed7e2;
  color: #97266d;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
`;

const SaveButton = styled.button`
  background: #667eea;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
`;

const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

function QuietHours({ userId, onUpdate }) {
  const [quietHours, setQuietHours] = useState({
    start_time: '22:00',
    end_time: '08:00',
    timezone: 'UTC',
    days_of_week: [0, 1, 2, 3, 4, 5, 6],
    exceptions: ['security', 'critical']
  });

  const toggleDay = (dayIndex) => {
    const newDays = quietHours.days_of_week.includes(dayIndex)
      ? quietHours.days_of_week.filter(d => d !== dayIndex)
      : [...quietHours.days_of_week, dayIndex];
    
    setQuietHours({ ...quietHours, days_of_week: newDays });
  };

  const saveQuietHours = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`/api/v1/preferences/${userId}/quiet-hours`, quietHours);
      onUpdate();
    } catch (error) {
      console.error('Error saving quiet hours:', error);
    }
  };

  return (
    <Form onSubmit={saveQuietHours}>
      <p style={{ color: '#718096', margin: '0 0 1rem 0' }}>
        Set when you don't want to receive notifications
      </p>
      
      <TimeInputs>
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
            Start Time
          </label>
          <Input
            type="time"
            value={quietHours.start_time}
            onChange={(e) => setQuietHours({ ...quietHours, start_time: e.target.value })}
          />
        </div>
        
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
            End Time
          </label>
          <Input
            type="time"
            value={quietHours.end_time}
            onChange={(e) => setQuietHours({ ...quietHours, end_time: e.target.value })}
          />
        </div>
      </TimeInputs>

      <div>
        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
          Timezone
        </label>
        <Input
          type="text"
          value={quietHours.timezone}
          onChange={(e) => setQuietHours({ ...quietHours, timezone: e.target.value })}
          placeholder="UTC, America/New_York, etc."
        />
      </div>

      <div>
        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
          Active Days
        </label>
        <DaysSelector>
          {days.map((day, index) => (
            <DayButton
              key={day}
              type="button"
              selected={quietHours.days_of_week.includes(index)}
              onClick={() => toggleDay(index)}
            >
              {day}
            </DayButton>
          ))}
        </DaysSelector>
      </div>

      <div>
        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
          Exceptions (these will override quiet hours)
        </label>
        <ExceptionsList>
          {quietHours.exceptions.map(exception => (
            <ExceptionTag key={exception}>
              {exception}
            </ExceptionTag>
          ))}
        </ExceptionsList>
      </div>

      <SaveButton type="submit">
        Save Quiet Hours
      </SaveButton>
    </Form>
  );
}

export default QuietHours;
