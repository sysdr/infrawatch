import React, { useState, useEffect } from 'react';
import {
  Container, AppBar, Toolbar, Typography, Grid, Paper, Button,
  Card, CardContent, Box, Chip, CircularProgress, Alert
} from '@mui/material';
import { Timeline, BubbleChart, Assessment, Speed } from '@mui/icons-material';
import CorrelationMatrix from './components/CorrelationMatrix';
import DependencyGraph from './components/DependencyGraph';
import RootCausePanel from './components/RootCausePanel';
import ImpactAssessment from './components/ImpactAssessment';
import apiService from './services/apiService';
import './App.css';

function App() {
  const [summary, setSummary] = useState(null);
  const [correlations, setCorrelations] = useState([]);
  const [rootCauses, setRootCauses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [summaryData, correlationsData] = await Promise.all([
        apiService.getDashboardSummary(),
        apiService.getCorrelations()
      ]);
      
      setSummary(summaryData);
      setCorrelations(correlationsData);
      // Only update root causes from summary when we have new data (don't overwrite with empty)
      setRootCauses(prev =>
        (summaryData.recent_root_causes?.length > 0)
          ? summaryData.recent_root_causes
          : prev
      );
      
      setLoading(false);
    } catch (error) {
      console.error('Error loading data:', error);
      setLoading(false);
    }
  };

  const handleGenerateSample = async () => {
    setAnalyzing(true);
    setMessage({ type: 'info', text: 'Generating sample metrics...' });
    
    try {
      await apiService.generateSampleMetrics();
      setMessage({ type: 'success', text: 'Sample metrics generated successfully!' });
      setTimeout(() => loadData(), 2000);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to generate sample metrics' });
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDetectCorrelations = async () => {
    setAnalyzing(true);
    setMessage({ type: 'info', text: 'Detecting correlations...' });
    
    try {
      const result = await apiService.detectCorrelations();
      setMessage({ 
        type: 'success', 
        text: `Detected ${result.correlations_detected} correlations!` 
      });
      setTimeout(() => loadData(), 2000);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to detect correlations' });
    } finally {
      setAnalyzing(false);
    }
  };

  const handleAnalyzeRootCause = async () => {
    setAnalyzing(true);
    setMessage({ type: 'info', text: 'Analyzing root causes...' });
    
    try {
      const result = await apiService.analyzeRootCause();
      const causes = result.root_causes || [];
      setRootCauses(causes);
      setMessage({ 
        type: 'success', 
        text: causes.length
          ? `Identified ${causes.length} root cause(s). Check Root Cause Analysis and Impact Assessment tabs.`
          : 'No root causes met the threshold. Generate sample data and detect correlations first.'
      });
      // Refresh summary/correlations but keep root causes we just set (loadData won't overwrite with empty)
      setTimeout(() => loadData(), 1500);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to analyze root causes' });
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <div className="App">
      <AppBar position="static" sx={{ background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)' }}>
        <Toolbar>
          <BubbleChart sx={{ mr: 2 }} />
          <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            Correlation Analysis Dashboard
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            Day 109: Advanced Metrics Intelligence
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {message && (
          <Alert 
            severity={message.type} 
            onClose={() => setMessage(null)}
            sx={{ mb: 3 }}
          >
            {message.text}
          </Alert>
        )}

        {/* Action Buttons */}
        <Paper elevation={2} sx={{ p: 2, mb: 3, background: 'rgba(255,255,255,0.95)' }}>
          <Grid container spacing={2}>
            <Grid item>
              <Button 
                variant="contained" 
                color="primary"
                onClick={handleGenerateSample}
                disabled={analyzing}
                startIcon={<Speed />}
              >
                Generate Sample Data
              </Button>
            </Grid>
            <Grid item>
              <Button 
                variant="contained" 
                color="secondary"
                onClick={handleDetectCorrelations}
                disabled={analyzing}
                startIcon={<Timeline />}
              >
                Detect Correlations
              </Button>
            </Grid>
            <Grid item>
              <Button 
                variant="contained" 
                color="success"
                onClick={handleAnalyzeRootCause}
                disabled={analyzing}
                startIcon={<Assessment />}
              >
                Analyze Root Causes
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* Summary Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={3} sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
              <CardContent>
                <Typography variant="h4" fontWeight="bold">
                  {summary?.total_metrics || 0}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Total Metrics
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={3} sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
              <CardContent>
                <Typography variant="h4" fontWeight="bold">
                  {summary?.active_correlations || 0}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Active Correlations
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={3} sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
              <CardContent>
                <Typography variant="h4" fontWeight="bold">
                  {summary?.total_correlations || 0}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Total Detected
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={3} sx={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', color: 'white' }}>
              <CardContent>
                <Typography variant="h4" fontWeight="bold">
                  {summary?.root_causes_identified || 0}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Root Causes
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Main Content Grid */}
        <Grid container spacing={3}>
          {/* Correlation Matrix */}
          <Grid item xs={12} lg={8}>
            <Paper elevation={3} sx={{ p: 3, minHeight: 400, background: 'rgba(255,255,255,0.95)' }}>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Correlation Matrix
              </Typography>
              <CorrelationMatrix correlations={correlations} />
            </Paper>
          </Grid>

          {/* Root Cause Panel */}
          <Grid item xs={12} lg={4}>
            <Paper elevation={3} sx={{ p: 3, minHeight: 400, background: 'rgba(255,255,255,0.95)' }}>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Root Cause Analysis
              </Typography>
              <RootCausePanel rootCauses={rootCauses} />
            </Paper>
          </Grid>

          {/* Dependency Graph */}
          <Grid item xs={12} lg={7}>
            <Paper elevation={3} sx={{ p: 3, minHeight: 500, background: 'rgba(255,255,255,0.95)' }}>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Dependency Network
              </Typography>
              <DependencyGraph correlations={correlations} />
            </Paper>
          </Grid>

          {/* Impact Assessment */}
          <Grid item xs={12} lg={5}>
            <Paper elevation={3} sx={{ p: 3, minHeight: 500, background: 'rgba(255,255,255,0.95)' }}>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Impact Assessment
              </Typography>
              <ImpactAssessment rootCauses={rootCauses} />
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </div>
  );
}

export default App;
