import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Alert,
  IconButton,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Rule as RuleIcon,
  Refresh as RefreshIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';
import { alertService } from '../services/alertService';

interface AlertStats {
  totalRules: number;
  activeAlerts: number;
  criticalAlerts: number;
  warningAlerts: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<AlertStats>({
    totalRules: 0,
    activeAlerts: 0,
    criticalAlerts: 0,
    warningAlerts: 0
  });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(() => {
      loadDashboardData(true);
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = useCallback(async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    setError(null);

    try {
      const [rules, alerts] = await Promise.all([
        alertService.getAlertRules(),
        alertService.getActiveAlerts()
      ]);

      const criticalCount = alerts.filter((alert: any) => 
        alert.rule?.severity === 'critical'
      ).length;
      
      const warningCount = alerts.filter((alert: any) => 
        alert.rule?.severity === 'warning'
      ).length;

      setStats({
        totalRules: rules.length,
        activeAlerts: alerts.length,
        criticalAlerts: criticalCount,
        warningAlerts: warningCount
      });
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  const handleManualRefresh = () => {
    loadDashboardData(true);
  };

  const StatCard: React.FC<{
    title: string;
    value: number;
    icon: React.ReactNode;
    color: string;
    isRefreshing?: boolean;
  }> = ({ title, value, icon, color, isRefreshing = false }) => (
    <Card sx={{ height: '100%', position: 'relative' }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={1}>
          <Box sx={{ color, mr: 1 }}>{icon}</Box>
          <Typography variant="h6" component="div">
            {title}
          </Typography>
          {isRefreshing && (
            <CircularProgress size={16} sx={{ ml: 1, color: 'primary.main' }} />
          )}
        </Box>
        <Typography variant="h3" component="div" sx={{ color }}>
          {value}
        </Typography>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Typography>Loading...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" gutterBottom>
          Alert Management Dashboard
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          {lastUpdated && (
            <Box display="flex" alignItems="center" gap={1}>
              <ScheduleIcon fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </Typography>
            </Box>
          )}
          <Tooltip title="Refresh data">
            <IconButton 
              onClick={handleManualRefresh} 
              disabled={refreshing}
              color="primary"
            >
              <RefreshIcon className={refreshing ? 'rotating' : ''} />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Rules"
            value={stats.totalRules}
            icon={<RuleIcon />}
            color="#0073aa"
            isRefreshing={refreshing}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Alerts"
            value={stats.activeAlerts}
            icon={<WarningIcon />}
            color="#ff9800"
            isRefreshing={refreshing}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Critical Alerts"
            value={stats.criticalAlerts}
            icon={<ErrorIcon />}
            color="#f44336"
            isRefreshing={refreshing}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Warning Alerts"
            value={stats.warningAlerts}
            icon={<CheckCircleIcon />}
            color="#4caf50"
            isRefreshing={refreshing}
          />
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            System Status
          </Typography>
          {stats.activeAlerts === 0 ? (
            <Alert severity="success">
              All systems operating normally - no active alerts
            </Alert>
          ) : (
            <Alert severity="warning">
              {stats.activeAlerts} active alert{stats.activeAlerts !== 1 ? 's' : ''} requiring attention
            </Alert>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Dashboard;
