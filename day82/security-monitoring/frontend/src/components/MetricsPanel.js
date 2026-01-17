import React from 'react';
import { Box, Grid, Paper, Typography } from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

function MetricsPanel({ summary }) {
  // Generate sample trend data (in production, this would come from API)
  const trendData = Array.from({ length: 24 }, (_, i) => ({
    hour: `${i}:00`,
    events: Math.floor(Math.random() * 1000) + 500,
    threats: Math.floor(Math.random() * 50)
  }));

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom fontWeight="bold">
            24-Hour Trend Analysis
          </Typography>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="events"
                stroke="#2196f3"
                strokeWidth={2}
                name="Security Events"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="threats"
                stroke="#f44336"
                strokeWidth={2}
                name="Threats Detected"
              />
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>
    </Grid>
  );
}

export default MetricsPanel;
