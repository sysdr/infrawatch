import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Paper, Typography, Box } from '@mui/material';

const CPUChart = ({ config = {} }) => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const generateData = () => {
      const newData = [...data];
      const timestamp = new Date().toLocaleTimeString();
      const cpuUsage = Math.floor(Math.random() * 100);
      
      newData.push({ time: timestamp, cpu: cpuUsage });
      if (newData.length > 20) newData.shift();
      
      setData(newData);
    };

    const interval = setInterval(generateData, config.refreshInterval || 5000);
    generateData();

    return () => clearInterval(interval);
  }, [config.refreshInterval]);

  return (
    <Paper sx={{ height: '100%', p: 2.5, display: 'flex', flexDirection: 'column', bgcolor: 'transparent', boxShadow: 'none' }}>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: '#1e293b' }}>
        CPU Usage
      </Typography>
      <Box sx={{ flexGrow: 1 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="time" stroke="#64748b" />
            <YAxis domain={[0, 100]} stroke="#64748b" />
            <Tooltip 
              contentStyle={{
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
              }}
            />
            <Line 
              type="monotone" 
              dataKey="cpu" 
              stroke="#10b981" 
              strokeWidth={3}
              dot={{ fill: '#10b981', r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default CPUChart;
