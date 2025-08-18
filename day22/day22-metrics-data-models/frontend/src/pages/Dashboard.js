import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  Box,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import metricsService from '../services/metricsService';

const Dashboard = () => {
  const [metrics, setMetrics] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [selectedMetric, setSelectedMetric] = useState('');
  const [metricData, setMetricData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      // Generate sample metrics
      await generateSampleMetrics();
      
      // Search for metrics
      const results = await metricsService.searchMetrics('cpu');
      setSearchResults(results);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const generateSampleMetrics = async () => {
    const sampleMetrics = [
      { name: 'cpu.usage', type: 'gauge', tags: { host: 'web-01', env: 'prod' } },
      { name: 'memory.usage', type: 'gauge', tags: { host: 'web-01', env: 'prod' } },
      { name: 'request.count', type: 'counter', tags: { service: 'api', env: 'prod' } },
      { name: 'response.time', type: 'histogram', tags: { service: 'api', env: 'prod' } },
    ];

    for (const metric of sampleMetrics) {
      // Generate data points
      for (let i = 0; i < 100; i++) {
        const timestamp = new Date(Date.now() - (100 - i) * 60000); // 1 minute intervals
        let value;
        
        switch (metric.type) {
          case 'gauge':
            value = Math.random() * 100;
            break;
          case 'counter':
            value = Math.floor(Math.random() * 1000);
            break;
          case 'histogram':
            value = Math.random() * 500 + 50;
            break;
          default:
            value = Math.random() * 100;
        }

        await metricsService.storeMetric({
          metric_name: metric.name,
          metric_type: metric.type,
          value: value,
          timestamp: timestamp,
          tags: metric.tags
        });
      }
    }
  };

  const handleSearch = async () => {
    try {
      const results = await metricsService.searchMetrics(searchTerm);
      setSearchResults(results);
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  const handleMetricSelect = async (metricName) => {
    try {
      setSelectedMetric(metricName);
      
      const endTime = new Date();
      const startTime = new Date(endTime.getTime() - 4 * 60 * 60 * 1000); // 4 hours ago
      
      const data = await metricsService.queryMetrics({
        metric_name: metricName,
        start_time: startTime,
        end_time: endTime
      });

      const chartData = data.data.map(point => ({
        timestamp: new Date(point.timestamp).getTime(),
        value: point.value,
        formattedTime: new Date(point.timestamp).toLocaleTimeString()
      }));

      setMetricData(chartData);
    } catch (error) {
      console.error('Error loading metric data:', error);
    }
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Metrics Dashboard
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Monitor your infrastructure metrics in real-time
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Search Section */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Metric Search
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <TextField
                  label="Search metrics"
                  variant="outlined"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  sx={{ flexGrow: 1 }}
                />
                <Button variant="contained" onClick={handleSearch}>
                  Search
                </Button>
              </Box>
              
              {searchResults.length > 0 && (
                <FormControl fullWidth>
                  <InputLabel>Select Metric</InputLabel>
                  <Select
                    value={selectedMetric}
                    onChange={(e) => handleMetricSelect(e.target.value)}
                    label="Select Metric"
                  >
                    {searchResults.map((metric) => (
                      <MenuItem key={metric.name} value={metric.name}>
                        {metric.name} ({metric.type}) - {metric.data_points} points
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Chart Section */}
        {selectedMetric && metricData.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {selectedMetric}
                </Typography>
                <Box sx={{ height: 400 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={metricData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="formattedTime"
                        tick={{ fontSize: 12 }}
                      />
                      <YAxis />
                      <Tooltip />
                      <Line 
                        type="monotone" 
                        dataKey="value" 
                        stroke="#0073aa" 
                        strokeWidth={2}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Stats Cards */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Metrics
              </Typography>
              <Typography variant="h4">
                {searchResults.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Data Points
              </Typography>
              <Typography variant="h4">
                {searchResults.reduce((sum, metric) => sum + metric.data_points, 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Active Metrics
              </Typography>
              <Typography variant="h4">
                {searchResults.filter(m => new Date(m.last_seen) > Date.now() - 300000).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
