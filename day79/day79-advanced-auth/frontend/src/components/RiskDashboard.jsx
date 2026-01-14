import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Alert
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import axios from 'axios';

const RiskDashboard = ({ userId }) => {
  const [riskHistory, setRiskHistory] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchRiskHistory();
  }, []);

  const fetchRiskHistory = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/auth/risk/history?user_id=${userId}&limit=50`
      );
      setRiskHistory(response.data.events);
    } catch (err) {
      setError('Failed to load risk history');
    }
  };

  const chartData = riskHistory.map((event, index) => ({
    index: index + 1,
    score: event.risk_score,
    timestamp: new Date(event.timestamp).toLocaleTimeString()
  }));

  const getRiskColor = (score) => {
    if (score >= 80) return 'error';
    if (score >= 60) return 'warning';
    if (score >= 30) return 'info';
    return 'success';
  };

  return (
    <Box sx={{ maxWidth: 1200, margin: '0 auto', mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        Risk Assessment Dashboard
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Score History
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="index" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="score"
                    stroke="#8884d8"
                    name="Risk Score"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Events
              </Typography>
              {riskHistory.slice(0, 10).map((event, index) => (
                <Alert
                  key={index}
                  severity={getRiskColor(event.risk_score)}
                  sx={{ mb: 1 }}
                >
                  Score: {event.risk_score} | Action: {event.action} | 
                  IP: {event.ip} | {new Date(event.timestamp).toLocaleString()}
                </Alert>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default RiskDashboard;
