import React from 'react';
import { Card, CardContent, Grid, Typography } from '@mui/material';

const MetricCard = ({ label, value }) => (
  <Card>
    <CardContent>
      <Typography variant="h6">{label}</Typography>
      <Typography variant="h4">{value}</Typography>
    </CardContent>
  </Card>
);

const ServerMetrics = ({ metrics }) => {
  if (!metrics) return null;
  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={3}><MetricCard label="Total" value={metrics.total_servers} /></Grid>
      <Grid item xs={12} sm={6} md={3}><MetricCard label="Healthy" value={metrics.healthy_count} /></Grid>
      <Grid item xs={12} sm={6} md={3}><MetricCard label="Warning" value={metrics.warning_count} /></Grid>
      <Grid item xs={12} sm={6} md={3}><MetricCard label="Critical" value={metrics.critical_count} /></Grid>
    </Grid>
  );
};

export default ServerMetrics;
