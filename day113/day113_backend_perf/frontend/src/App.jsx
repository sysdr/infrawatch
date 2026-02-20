import React from 'react';
import { Box, Grid, Typography, Chip, CircularProgress, Alert, AppBar, Toolbar } from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import SpeedIcon from '@mui/icons-material/Speed';
import { usePerformance } from './hooks/usePerformance';
import LatencyChart from './components/LatencyChart';
import StatCard from './components/StatCard';
import CachePanel from './components/CachePanel';
import PoolPanel from './components/PoolPanel';
import SystemPanel from './components/SystemPanel';

const theme = createTheme({
  palette: { primary: { main: '#2e7d32' }, secondary: { main: '#26a69a' } },
  typography: { fontFamily: '"Inter", "Segoe UI", sans-serif' },
});

export default function App() {
  const { data, history, error } = usePerformance(3000);

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ minHeight: '100vh', bgcolor: '#f8fdf8' }}>
        <AppBar position="static" elevation={0} sx={{ bgcolor: '#1b5e20' }}>
          <Toolbar>
            <SpeedIcon sx={{ mr: 1.5, color: '#a5d6a7' }} />
            <Typography variant="h6" fontWeight={700} color="white" sx={{ flexGrow: 1 }}>
              Backend Performance Monitor
            </Typography>
            <Chip
              label={data ? 'LIVE' : 'CONNECTING'}
              size="small"
              sx={{ bgcolor: data ? '#a5d6a7' : '#ffcc02', color: '#1b5e20', fontWeight: 700 }}
            />
          </Toolbar>
        </AppBar>

        <Box sx={{ p: { xs: 2, md: 3 } }}>
          <Typography variant="caption" color="text.secondary">
            Day 113 — Week 11 · Profiling · Query Optimization · Caching · Connection Pooling
          </Typography>

          {error && (
            <Alert severity="warning" sx={{ mt: 1, mb: 2, borderRadius: 2 }}>
              Backend unreachable: {error}. Start the FastAPI server to see live data.
            </Alert>
          )}

          {!data && !error && (
            <Box display="flex" justifyContent="center" mt={8}>
              <CircularProgress color="primary" />
            </Box>
          )}

          {data && (
            <>
              <Grid container spacing={2} mt={0.5}>
                <Grid item xs={6} sm={3}>
                  <StatCard title="p50 Latency" value={data.latency.p50_ms} unit="ms"
                    max={200} color="#2e7d32" subtitle="median response" />
                </Grid>
                <Grid item xs={6} sm={3}>
                  <StatCard title="p99 Latency" value={data.latency.p99_ms} unit="ms"
                    max={500} color="#1b5e20" subtitle="tail latency" />
                </Grid>
                <Grid item xs={6} sm={3}>
                  <StatCard title="Cache Hit Rate" value={data.cache.hit_rate_pct} unit="%"
                    max={100} color="#26a69a" subtitle="target >= 85%" />
                </Grid>
                <Grid item xs={6} sm={3}>
                  <StatCard title="Total Requests" value={data.latency.total_requests} unit=""
                    color="#388e3c" subtitle={`avg ${data.latency.avg_ms} ms`} />
                </Grid>
              </Grid>

              <Grid container spacing={2} mt={0.5}>
                <Grid item xs={12} md={8}>
                  <LatencyChart history={history} />
                </Grid>
                <Grid item xs={12} md={4}>
                  <SystemPanel data={data} />
                </Grid>
              </Grid>

              <Grid container spacing={2} mt={0.5}>
                <Grid item xs={12} md={6}>
                  <CachePanel data={data} />
                </Grid>
                <Grid item xs={12} md={6}>
                  <PoolPanel data={data} />
                </Grid>
              </Grid>
            </>
          )}
        </Box>
      </Box>
    </ThemeProvider>
  );
}
