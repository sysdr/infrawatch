import React, { useState, useEffect } from 'react';
import { useRealtime } from '../../contexts/RealtimeContext';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Users } from 'lucide-react';

function LiveUserCount() {
  const { userCount, connectionStatus } = useRealtime();
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (userCount > 0) {
      setHistory(prev => {
        const newHistory = [
          ...prev,
          { time: new Date().getTime(), count: userCount }
        ];
        // Keep last 20 data points
        return newHistory.slice(-20);
      });
    }
  }, [userCount]);

  return (
    <div className="live-count-container">
      <div className="count-display">
        <Users size={32} color="#3b82f6" />
        <div className="count-value">{userCount.toLocaleString()}</div>
        {connectionStatus !== 'connected' && (
          <div className="stale-indicator">Stale data</div>
        )}
      </div>
      
      <div className="sparkline">
        <ResponsiveContainer width="100%" height={80}>
          <LineChart data={history}>
            <XAxis dataKey="time" hide />
            <YAxis hide domain={['auto', 'auto']} />
            <Tooltip 
              labelFormatter={(value) => new Date(value).toLocaleTimeString()}
              formatter={(value) => [`${value} users`, 'Count']}
            />
            <Line 
              type="monotone" 
              dataKey="count" 
              stroke="#3b82f6" 
              strokeWidth={2}
              dot={false}
              isAnimationActive={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default LiveUserCount;
