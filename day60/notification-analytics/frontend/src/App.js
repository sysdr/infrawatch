import React, { useState } from 'react';
import { Container, Grid, Paper, Typography, Box, Tabs, Tab } from '@mui/material';
import StatisticsPanel from './components/analytics/StatisticsPanel';
import AnomaliesPanel from './components/anomalies/AnomaliesPanel';
import PredictionsChart from './components/predictions/PredictionsChart';
import CorrelationMatrix from './components/correlations/CorrelationMatrix';

function App() {
  const [activeTab, setActiveTab] = useState(0);
  const [metrics] = useState([
    'notification_delivery_time',
    'notification_failure_rate',
    'notification_volume'
  ]);
  const [selectedMetric, setSelectedMetric] = useState(metrics[0]);

  return (
    <Box sx={{ bgcolor: '#f8f9fa', minHeight: '100vh', py: 3 }}>
      <Container maxWidth="xl">
        <Paper elevation={2} sx={{ p: 3, mb: 3, bgcolor: 'white', borderRadius: 2, border: '1px solid #e5e7eb' }}>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, color: '#1f2937', letterSpacing: '-0.02em' }}>
            📊 Advanced Analytics Dashboard
          </Typography>
          <Typography variant="body2" sx={{ color: '#6b7280', mt: 0.5 }}>
            Real-time statistical analysis, anomaly detection, and predictive insights
          </Typography>
        </Paper>

        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          sx={{ 
            bgcolor: 'white', 
            borderRadius: 2, 
            mb: 3,
            border: '1px solid #e5e7eb',
            '& .MuiTab-root': {
              color: '#6b7280',
              fontWeight: 500,
              '&.Mui-selected': {
                color: '#059669',
                fontWeight: 600
              }
            },
            '& .MuiTabs-indicator': {
              backgroundColor: '#059669',
              height: 3
            }
          }}
        >
          <Tab label="Statistics" />
          <Tab label="Anomalies" />
          <Tab label="Predictions" />
          <Tab label="Correlations" />
        </Tabs>

        {activeTab === 0 && (
          <StatisticsPanel metrics={metrics} selectedMetric={selectedMetric} onMetricChange={setSelectedMetric} />
        )}
        {activeTab === 1 && <AnomaliesPanel metrics={metrics} />}
        {activeTab === 2 && (
          <PredictionsChart metrics={metrics} selectedMetric={selectedMetric} onMetricChange={setSelectedMetric} />
        )}
        {activeTab === 3 && <CorrelationMatrix metrics={metrics} selectedMetric={selectedMetric} />}
      </Container>
    </Box>
  );
}

export default App;
