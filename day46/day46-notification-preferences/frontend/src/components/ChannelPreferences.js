import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Mail, MessageSquare, Smartphone, Bell } from 'lucide-react';
import axios from 'axios';

const ChannelList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const ChannelItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border: 2px solid ${props => props.enabled ? '#10b981' : '#e5e7eb'}; /* emerald-500 | gray-200 */
  border-radius: 8px;
  background: ${props => props.enabled ? '#ecfdf5' : '#f9fafb'}; /* emerald-50 */
`;

const ChannelInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
`;

const PrioritySlider = styled.input`
  width: 100px;
`;

const Toggle = styled.input`
  width: 20px;
  height: 20px;
`;

const SaveButton = styled.button`
  background: #4f46e5; /* indigo-600 */
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 1rem;
  font-weight: 600;
`;

const channelIcons = {
  email: Mail,
  sms: MessageSquare,
  push: Smartphone,
  in_app: Bell
};

function ChannelPreferences({ userId, preferences, onUpdate }) {
  const [channels, setChannels] = useState([
    { channel: 'email', priority_score: 80, is_enabled: true },
    { channel: 'push', priority_score: 70, is_enabled: true },
    { channel: 'sms', priority_score: 60, is_enabled: false },
    { channel: 'in_app', priority_score: 90, is_enabled: true }
  ]);

  const updateChannel = (index, field, value) => {
    const newChannels = [...channels];
    newChannels[index][field] = value;
    setChannels(newChannels);
  };

  const savePreferences = async () => {
    try {
      await axios.put(`/api/v1/preferences/${userId}/channels`, channels);
      onUpdate();
    } catch (error) {
      console.error('Error saving channel preferences:', error);
    }
  };

  return (
    <div>
      <p style={{ color: '#718096', marginBottom: '1rem' }}>
        Set priority scores (0-100) for each notification channel
      </p>
      
      <ChannelList>
        {channels.map((channel, index) => {
          const IconComponent = channelIcons[channel.channel];
          return (
            <ChannelItem key={channel.channel} enabled={channel.is_enabled}>
              <ChannelInfo>
                <IconComponent size={20} />
                <div>
                  <strong>{channel.channel.toUpperCase()}</strong>
                  <div style={{ fontSize: '0.85rem', color: '#718096' }}>
                    Priority: {channel.priority_score}
                  </div>
                </div>
              </ChannelInfo>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <PrioritySlider
                  type="range"
                  min="0"
                  max="100"
                  value={channel.priority_score}
                  onChange={(e) => updateChannel(index, 'priority_score', parseInt(e.target.value))}
                  disabled={!channel.is_enabled}
                />
                <Toggle
                  type="checkbox"
                  checked={channel.is_enabled}
                  onChange={(e) => updateChannel(index, 'is_enabled', e.target.checked)}
                />
              </div>
            </ChannelItem>
          );
        })}
      </ChannelList>
      
      <SaveButton onClick={savePreferences}>
        Save Channel Preferences
      </SaveButton>
    </div>
  );
}

export default ChannelPreferences;
