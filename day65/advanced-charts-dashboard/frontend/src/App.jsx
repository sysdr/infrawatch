import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Tabs,
  Tab,
  CircularProgress
} from '@mui/material';
import MultiSeriesChart from './components/charts/MultiSeriesChart';
import StackedChart from './components/charts/StackedChart';
import ScatterPlot from './components/charts/ScatterPlot';
import HeatmapChart from './components/charts/HeatmapChart';
import LatencyDistribution from './components/charts/LatencyDistribution';
import StatusTimeline from './components/charts/StatusTimeline';
import { chartService } from './services/chartService';

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index} style={{ paddingTop: 20 }}>
      {value === index && children}
    </div>
  );
}

function App() {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState({
    multiSeries: null,
    stacked: null,
    scatter: null,
    heatmap: null,
    latency: null,
    timeline: null
  });

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [multiSeries, stacked, scatter, heatmap, latency, timeline] = await Promise.all([
        chartService.getMultiSeriesData(['cpu_usage', 'memory_usage', 'disk_io']),
        chartService.getStackedData(['Q1', 'Q2', 'Q3', 'Q4'], ['revenue', 'costs', 'profit']),
        chartService.getScatterData('request_count', 'latency_ms'),
        chartService.getHeatmapData('api_requests'),
        chartService.getLatencyDistribution(),
        chartService.getStatusTimeline()
      ]);

      setData({ multiSeries, stacked, scatter, heatmap, latency, timeline });
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom fontWeight="bold">
          Advanced Charts Dashboard
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Production-grade visualization components for infrastructure monitoring
        </Typography>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="Multi-Series" />
          <Tab label="Stacked" />
          <Tab label="Scatter & Correlation" />
          <Tab label="Heatmap" />
          <Tab label="Custom Charts" />
        </Tabs>
      </Paper>

      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress size={60} />
        </Box>
      ) : (
        <>
          <TabPanel value={tabValue} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>System Metrics Over Time</Typography>
                  {data.multiSeries && <MultiSeriesChart data={data.multiSeries} />}
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>Quarterly Financial Performance</Typography>
                  {data.stacked && <StackedChart data={data.stacked} />}
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>Request Volume vs Latency</Typography>
                  {data.scatter && <ScatterPlot data={data.scatter} />}
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>API Requests by Time of Day</Typography>
                  {data.heatmap && <HeatmapChart data={data.heatmap} />}
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={4}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>Latency Distribution by Service</Typography>
                  {data.latency && <LatencyDistribution data={data.latency} />}
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>Service Status Timeline</Typography>
                  {data.timeline && <StatusTimeline data={data.timeline} />}
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>
        </>
      )}
    </Container>
  );
}

export default App;
