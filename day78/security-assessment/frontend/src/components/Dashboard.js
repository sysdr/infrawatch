import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Security,
  BugReport,
  VerifiedUser,
  Warning,
  PlayArrow,
} from '@mui/icons-material';
import { securityAPI } from '../services/api';
import VulnerabilityList from './VulnerabilityList';
import ComplianceView from './ComplianceView';
import ThreatMatrix from './ThreatMatrix';

const Dashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [scanStatus, setScanStatus] = useState('');

  useEffect(() => {
    loadMetrics();
    const interval = setInterval(loadMetrics, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadMetrics = async () => {
    try {
      const response = await securityAPI.getDashboardMetrics();
      setMetrics(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load metrics:', error);
      setLoading(false);
    }
  };

  const runFullScan = async () => {
    setScanning(true);
    setScanStatus('Running comprehensive security assessment...');
    
    try {
      await securityAPI.runFullScan();
      setScanStatus('Scan completed successfully!');
      setTimeout(() => {
        loadMetrics();
        setScanning(false);
        setScanStatus('');
      }, 2000);
    } catch (error) {
      setScanStatus('Scan failed: ' + error.message);
      setScanning(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  const getSeverityColor = (count, total) => {
    const percentage = (count / total) * 100;
    if (percentage > 50) return 'error';
    if (percentage > 20) return 'warning';
    return 'success';
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 600, color: '#1a237e' }}>
          Security Assessment Platform
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Comprehensive security monitoring and vulnerability management
        </Typography>
      </Box>

      {/* Scan Control */}
      <Paper sx={{ p: 3, mb: 4, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <Grid container alignItems="center" spacing={2}>
          <Grid item xs={12} md={8}>
            <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
              Security Scan Control
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
              Last scan: {new Date().toLocaleString()}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4} sx={{ textAlign: 'right' }}>
            <Button
              variant="contained"
              size="large"
              startIcon={scanning ? <CircularProgress size={20} color="inherit" /> : <PlayArrow />}
              onClick={runFullScan}
              disabled={scanning}
              sx={{
                bgcolor: 'white',
                color: '#667eea',
                '&:hover': { bgcolor: 'rgba(255,255,255,0.9)' }
              }}
            >
              {scanning ? 'Scanning...' : 'Run Full Scan'}
            </Button>
          </Grid>
        </Grid>
        {scanStatus && (
          <Alert severity={scanning ? 'info' : 'success'} sx={{ mt: 2 }}>
            {scanStatus}
          </Alert>
        )}
      </Paper>

      {/* Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <BugReport sx={{ fontSize: 40, color: 'white', mr: 2 }} />
                <Typography variant="h4" sx={{ color: 'white', fontWeight: 600 }}>
                  {metrics?.vulnerabilities?.total || 0}
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
                Vulnerabilities
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
                {metrics?.vulnerabilities?.critical || 0} critical, {metrics?.vulnerabilities?.open || 0} open
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <VerifiedUser sx={{ fontSize: 40, color: 'white', mr: 2 }} />
                <Typography variant="h4" sx={{ color: 'white', fontWeight: 600 }}>
                  {metrics?.compliance?.score || 0}%
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
                Compliance Score
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
                {metrics?.compliance?.passed || 0}/{metrics?.compliance?.total_checks || 0} checks passed
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Warning sx={{ fontSize: 40, color: 'white', mr: 2 }} />
                <Typography variant="h4" sx={{ color: 'white', fontWeight: 600 }}>
                  {metrics?.threats?.total || 0}
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
                Threats Identified
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
                {metrics?.threats?.high_risk || 0} high risk threats
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Security sx={{ fontSize: 40, color: 'white', mr: 2 }} />
                <Typography variant="h4" sx={{ color: 'white', fontWeight: 600 }}>
                  {metrics?.activity?.scan_coverage || 0}%
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
                Scan Coverage
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
                MTTR: {metrics?.activity?.mean_time_to_remediate || 0}h
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detailed Views */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <VulnerabilityList />
        </Grid>
        <Grid item xs={12} md={6}>
          <ComplianceView />
        </Grid>
        <Grid item xs={12} md={6}>
          <ThreatMatrix />
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
