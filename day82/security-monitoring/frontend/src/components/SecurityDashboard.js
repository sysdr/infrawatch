import React from 'react';
import { Box, Grid, Typography } from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const COLORS = ['#f44336', '#ff9800', '#ffc107', '#4caf50', '#2196f3'];

function SecurityDashboard({ summary }) {
  const topAttacks = summary?.top_attacks || [];

  const attackData = topAttacks.map(attack => ({
    name: attack.attack_type?.replace(/_/g, ' ') || 'Unknown',
    count: attack.count || 0
  }));

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="subtitle1" gutterBottom fontWeight="bold">
            Top Attack Types (24h)
          </Typography>
          {attackData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={attackData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#f44336" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <Box sx={{ textAlign: 'center', py: 5, color: 'text.secondary' }}>
              <Typography>No threat data available</Typography>
            </Box>
          )}
        </Grid>

        <Grid item xs={12}>
          <Typography variant="subtitle1" gutterBottom fontWeight="bold">
            Threat Distribution
          </Typography>
          {attackData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={attackData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => entry.name}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {attackData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <Box sx={{ textAlign: 'center', py: 5, color: 'text.secondary' }}>
              <Typography>No distribution data available</Typography>
            </Box>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}

export default SecurityDashboard;
