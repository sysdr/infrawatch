import React, { useState, useEffect } from 'react';
import { Paper, Typography, Box, Grid, Card, CardContent, Button, CircularProgress } from '@mui/material';
import { complianceApi } from '../services/api';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';

function ComplianceReports() {
  const [metrics, setMetrics] = useState(null);
  const [gdprReport, setGdprReport] = useState(null);
  const [soc2Report, setSoc2Report] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadComplianceData();
  }, []);

  const loadComplianceData = async () => {
    try {
      const metricsRes = await complianceApi.getMetrics();
      setMetrics(metricsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading compliance data:', error);
      setLoading(false);
    }
  };

  const generateGDPRReport = async () => {
    try {
      const response = await complianceApi.getGDPRReport(90);
      setGdprReport(response.data);
    } catch (error) {
      console.error('Error generating GDPR report:', error);
    }
  };

  const generateSOC2Report = async () => {
    try {
      const response = await complianceApi.getSOC2Report(90);
      setSoc2Report(response.data);
    } catch (error) {
      console.error('Error generating SOC2 report:', error);
    }
  };

  if (loading) {
    return <CircularProgress />;
  }

  const isCompliant = metrics?.compliance_status === 'compliant';

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Compliance Reports
      </Typography>

      {/* Compliance Status */}
      <Card sx={{ mb: 3, bgcolor: isCompliant ? '#e8f5e9' : '#fff3e0' }}>
        <CardContent>
          <Box display="flex" alignItems="center">
            {isCompliant ? (
              <CheckCircleIcon sx={{ fontSize: 48, color: '#4caf50', mr: 2 }} />
            ) : (
              <WarningIcon sx={{ fontSize: 48, color: '#ff9800', mr: 2 }} />
            )}
            <Box>
              <Typography variant="h5">
                {isCompliant ? 'Compliant' : 'Review Required'}
              </Typography>
              <Typography variant="body2">
                Last 30 days compliance status
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Authentication Metrics
            </Typography>
            <Typography variant="body1">
              Total Attempts: {metrics?.authentication?.total_attempts || 0}
            </Typography>
            <Typography variant="body1">
              Failed Attempts: {metrics?.authentication?.failed_attempts || 0}
            </Typography>
            <Typography variant="body1">
              Failure Rate: {metrics?.authentication?.failure_rate || 0}%
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Incident Metrics
            </Typography>
            <Typography variant="body1">
              Total Incidents: {metrics?.incidents?.total || 0}
            </Typography>
            <Typography variant="body1">
              Critical: {metrics?.incidents?.critical || 0}
            </Typography>
            <Typography variant="body1">
              Resolved: {metrics?.incidents?.resolved || 0}
            </Typography>
            <Typography variant="body1">
              Resolution Rate: {metrics?.incidents?.resolution_rate || 0}%
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Report Generation */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Generate Compliance Reports
        </Typography>
        <Box display="flex" gap={2} mt={2}>
          <Button variant="contained" onClick={generateGDPRReport}>
            Generate GDPR Report
          </Button>
          <Button variant="contained" onClick={generateSOC2Report}>
            Generate SOC2 Report
          </Button>
        </Box>
      </Paper>

      {/* GDPR Report Display */}
      {gdprReport && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            GDPR Data Access Report
          </Typography>
          <Typography variant="body2">
            Period: {gdprReport.period.start} to {gdprReport.period.end}
          </Typography>
          <Typography variant="body2">
            Total Access Events: {gdprReport.total_access_events}
          </Typography>
          <Typography variant="body2">
            Unique Users: {gdprReport.unique_users}
          </Typography>
        </Paper>
      )}

      {/* SOC2 Report Display */}
      {soc2Report && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            SOC2 Access Control Report
          </Typography>
          <Typography variant="body2">
            Period: {soc2Report.period.start} to {soc2Report.period.end}
          </Typography>
          <Typography variant="body2">
            Failed Authorization Attempts: {soc2Report.failed_authorization_attempts}
          </Typography>
          <Typography variant="body2">
            Security Incidents: {soc2Report.security_incidents.total}
          </Typography>
        </Paper>
      )}
    </Box>
  );
}

export default ComplianceReports;
