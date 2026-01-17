import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Chip,
  Alert,
  Card,
  CardContent,
  LinearProgress
} from '@mui/material';
import {
  Security,
  Warning,
  CheckCircle,
  Error as ErrorIcon
} from '@mui/icons-material';
import SecurityDashboard from './components/SecurityDashboard';
import ThreatList from './components/ThreatList';
import EventTimeline from './components/EventTimeline';
import MetricsPanel from './components/MetricsPanel';
import { useSecurityMonitoring } from './hooks/useSecurityMonitoring';

function App() {
  const {
    summary,
    threats,
    events,
    isConnected,
    loading,
    error
  } = useSecurityMonitoring();

  const getSeverityColor = (severity) => {
    if (severity >= 80) return 'error';
    if (severity >= 60) return 'warning';
    return 'info';
  };

  return (
    <Box sx={{ bgcolor: '#f5f7fa', minHeight: '100vh', py: 3 }}>
      <Container maxWidth="xl">
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Security sx={{ fontSize: 40, color: '#1976d2' }} />
            <Typography variant="h4" fontWeight="bold" color="#1a237e">
              Security Monitoring System
            </Typography>
            <Chip
              icon={isConnected ? <CheckCircle /> : <ErrorIcon />}
              label={isConnected ? 'Connected' : 'Disconnected'}
              color={isConnected ? 'success' : 'error'}
              size="small"
            />
          </Box>
          <Typography variant="body2" color="text.secondary">
            Real-time threat detection and security event monitoring
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {loading && <LinearProgress sx={{ mb: 3 }} />}

        {/* Metrics Overview */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={3}>
            <Card sx={{ height: '100%', bgcolor: '#e3f2fd' }}>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>
                  Total Events (24h)
                </Typography>
                <Typography variant="h3" fontWeight="bold">
                  {summary?.events?.total_events?.toLocaleString() || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {summary?.events?.last_hour || 0} in last hour
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card sx={{ height: '100%', bgcolor: '#fff3e0' }}>
              <CardContent>
                <Typography variant="h6" color="warning.main" gutterBottom>
                  High Severity Events
                </Typography>
                <Typography variant="h3" fontWeight="bold" color="warning.main">
                  {summary?.events?.high_severity || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Requiring attention
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card sx={{ height: '100%', bgcolor: '#ffebee' }}>
              <CardContent>
                <Typography variant="h6" color="error.main" gutterBottom>
                  Active Threats
                </Typography>
                <Typography variant="h3" fontWeight="bold" color="error.main">
                  {summary?.threats?.active_threats || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Under investigation
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card sx={{ height: '100%', bgcolor: '#e8f5e9' }}>
              <CardContent>
                <Typography variant="h6" color="success.main" gutterBottom>
                  Auto Responded
                </Typography>
                <Typography variant="h3" fontWeight="bold" color="success.main">
                  {summary?.threats?.auto_responded || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Automated responses
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Main Dashboard */}
        <Grid container spacing={3}>
          <Grid item xs={12} lg={8}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                Security Events Timeline
              </Typography>
              <EventTimeline events={events} />
            </Paper>

            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                Threat Analysis
              </Typography>
              <SecurityDashboard summary={summary} />
            </Paper>
          </Grid>

          <Grid item xs={12} lg={4}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                Active Threats
              </Typography>
              <ThreatList threats={threats} />
            </Paper>
          </Grid>
        </Grid>

        {/* Metrics Panel */}
        <Box sx={{ mt: 3 }}>
          <MetricsPanel summary={summary} />
        </Box>
      </Container>
    </Box>
  );
}

export default App;
