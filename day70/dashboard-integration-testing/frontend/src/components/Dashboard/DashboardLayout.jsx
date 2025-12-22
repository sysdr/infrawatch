import React, { useState } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  AppBar,
  Toolbar,
  Chip,
  Button,
  ButtonGroup,
  Card,
  CardContent,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { green, red, orange } from '@mui/material/colors';
import SignalWifiStatusbar4BarIcon from '@mui/icons-material/SignalWifiStatusbar4Bar';
import SignalWifiOffIcon from '@mui/icons-material/SignalWifiOff';
import MetricChart from '../Charts/MetricChart';
import PerformancePanel from './PerformancePanel';
import { useDashboardStore } from '../../store/dashboardStore';
import { useWebSocket } from '../../hooks/useWebSocket';

export default function DashboardLayout({ isConnected }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));
  const displayMetrics = useDashboardStore((state) => state.displayMetrics);
  const performance = useDashboardStore((state) => state.performance);
  const { setLoadLevel } = useWebSocket();
  const [currentLoad, setCurrentLoad] = useState('normal');

  const handleLoadChange = (load) => {
    setCurrentLoad(load);
    setLoadLevel(load);
  };

  const metricNames = Object.keys(displayMetrics);
  const gridSize = isMobile ? 12 : isTablet ? 6 : 4;

  return (
    <Box>
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Dashboard Integration Testing
          </Typography>
          <Chip
            icon={isConnected ? <SignalWifiStatusbar4BarIcon /> : <SignalWifiOffIcon />}
            label={isConnected ? 'Connected' : 'Disconnected'}
            color={isConnected ? 'success' : 'error'}
            sx={{ mr: 2 }}
          />
          <ButtonGroup variant="outlined" size="small">
            <Button
              onClick={() => handleLoadChange('normal')}
              variant={currentLoad === 'normal' ? 'contained' : 'outlined'}
            >
              Normal
            </Button>
            <Button
              onClick={() => handleLoadChange('high')}
              variant={currentLoad === 'high' ? 'contained' : 'outlined'}
            >
              High
            </Button>
            <Button
              onClick={() => handleLoadChange('burst')}
              variant={currentLoad === 'burst' ? 'contained' : 'outlined'}
            >
              Burst
            </Button>
          </ButtonGroup>
        </Toolbar>
      </AppBar>

      <Box sx={{ p: isMobile ? 1 : 3 }}>
        <Grid container spacing={2}>
          {/* Performance Stats */}
          <Grid item xs={12}>
            <PerformancePanel stats={performance} />
          </Grid>

          {/* Metric Charts */}
          {metricNames.length === 0 ? (
            <Grid item xs={12}>
              <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="h6" color="text.secondary">
                  Waiting for metrics...
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Real-time data will appear here once the connection is established
                </Typography>
              </Paper>
            </Grid>
          ) : (
            metricNames.map((metricName) => (
              <Grid item xs={gridSize} key={metricName}>
                <MetricChart
                  name={metricName}
                  data={displayMetrics[metricName]}
                />
              </Grid>
            ))
          )}
        </Grid>
      </Box>
    </Box>
  );
}
