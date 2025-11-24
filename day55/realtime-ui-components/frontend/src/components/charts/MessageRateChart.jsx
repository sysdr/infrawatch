import React, { useState, useEffect } from 'react';
import { useRealtime } from '../../contexts/RealtimeContext';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function MessageRateChart() {
  const { messageRate } = useRealtime();
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (messageRate >= 0) {
      setHistory(prev => {
        const newHistory = [
          ...prev,
          { 
            time: new Date().toLocaleTimeString(), 
            rate: messageRate 
          }
        ];
        // Keep last 30 data points
        return newHistory.slice(-30);
      });
    }
  }, [messageRate]);

  return (
    <div className="chart-container">
      <div className="current-rate">
        <span className="rate-value">{messageRate.toFixed(2)}</span>
        <span className="rate-unit">msg/sec</span>
      </div>
      
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={history} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="time" 
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />
          <YAxis 
            tick={{ fontSize: 12 }}
            label={{ value: 'Messages/sec', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip />
          <Line 
            type="monotone" 
            dataKey="rate" 
            stroke="#8b5cf6" 
            strokeWidth={2}
            dot={false}
            isAnimationActive={true}
            animationDuration={300}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default MessageRateChart;
