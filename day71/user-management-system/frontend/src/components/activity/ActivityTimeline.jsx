import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Chip,
  Box,
  Grid
} from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';
import { activityAPI } from '../../services/api';

export default function ActivityTimeline() {
  const [activities, setActivities] = useState([]);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [activitiesRes, statsRes] = await Promise.all([
        activityAPI.getMyActivities({ limit: 20 }),
        activityAPI.getMyActivityStats(30)
      ]);
      setActivities(activitiesRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Failed to load activity data', err);
    }
  };

  const getActionColor = (action) => {
    if (action.startsWith('auth')) return 'primary';
    if (action.startsWith('dashboard')) return 'secondary';
    if (action.startsWith('profile')) return 'success';
    return 'default';
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Activity Timeline
      </Typography>

      {stats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Activity Over Time
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={stats.activity_timeline}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="count" stroke="#1976d2" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      )}

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent Activities
        </Typography>
        <List>
          {activities.map((activity) => (
            <ListItem
              key={activity.id}
              sx={{
                borderLeft: 3,
                borderColor: `${getActionColor(activity.action)}.main`,
                mb: 1,
                bgcolor: 'background.default'
              }}
            >
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                      label={activity.action}
                      size="small"
                      color={getActionColor(activity.action)}
                    />
                    <Typography variant="body2">
                      {activity.description || activity.action}
                    </Typography>
                  </Box>
                }
                secondary={format(new Date(activity.created_at), 'PPpp')}
              />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Container>
  );
}
