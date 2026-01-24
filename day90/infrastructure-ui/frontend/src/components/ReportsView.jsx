import React, { useState } from 'react';
import {
  Box, Paper, Typography, Button, Grid, Card, CardContent, CardActions,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  CircularProgress
} from '@mui/material';
import { Description, Download } from '@mui/icons-material';
import { reportsAPI } from '../services/api';

function ReportsView() {
  const [activeReport, setActiveReport] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);

  const reports = [
    { id: 'inventory', title: 'Resource Inventory', description: 'Complete list of all resources' },
    { id: 'utilization', title: 'Utilization Report', description: 'CPU and memory usage statistics' },
    { id: 'compliance', title: 'Compliance Report', description: 'Policy violations and recommendations' }
  ];

  const generateReport = async (reportId) => {
    setLoading(true);
    setActiveReport(reportId);
    
    try {
      let response;
      switch(reportId) {
        case 'inventory':
          response = await reportsAPI.getInventory();
          break;
        case 'utilization':
          response = await reportsAPI.getUtilization();
          break;
        case 'compliance':
          response = await reportsAPI.getCompliance();
          break;
      }
      setReportData(response.data);
    } catch (error) {
      console.error('Failed to generate report:', error);
    } finally {
      setLoading(false);
    }
  };

  const exportReport = () => {
    if (!reportData) return;
    
    const dataStr = JSON.stringify(reportData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${activeReport}-report-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Infrastructure Reports
      </Typography>

      <Grid container spacing={3}>
        {reports.map((report) => (
          <Grid item xs={12} md={4} key={report.id}>
            <Card elevation={3}>
              <CardContent>
                <Description sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                <Typography variant="h6" gutterBottom>
                  {report.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {report.description}
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  onClick={() => generateReport(report.id)}
                  disabled={loading && activeReport === report.id}
                >
                  Generate
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {loading && (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px" mt={3}>
          <CircularProgress />
        </Box>
      )}

      {!loading && reportData && (
        <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              {reports.find(r => r.id === activeReport)?.title}
            </Typography>
            <Button startIcon={<Download />} onClick={exportReport}>
              Export
            </Button>
          </Box>

          {activeReport === 'inventory' && (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Type</TableCell>
                    <TableCell>Provider</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Count</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {reportData.data?.map((row, idx) => (
                    <TableRow key={idx}>
                      <TableCell>{row.type}</TableCell>
                      <TableCell>{row.provider}</TableCell>
                      <TableCell>{row.status}</TableCell>
                      <TableCell align="right">{row.count}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {activeReport === 'utilization' && (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Resource Type</TableCell>
                    <TableCell align="right">Avg CPU %</TableCell>
                    <TableCell align="right">Avg Memory %</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {reportData.data?.map((row, idx) => (
                    <TableRow key={idx}>
                      <TableCell>{row.resource_type}</TableCell>
                      <TableCell align="right">{row.avg_cpu}</TableCell>
                      <TableCell align="right">{row.avg_memory}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {activeReport === 'compliance' && (
            <Box>
              <Typography variant="body1" gutterBottom>
                Total Violations: {reportData.total_violations}
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Resource</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Violation</TableCell>
                      <TableCell>Missing Tags</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {reportData.violations?.slice(0, 10).map((violation, idx) => (
                      <TableRow key={idx}>
                        <TableCell>{violation.name}</TableCell>
                        <TableCell>{violation.type}</TableCell>
                        <TableCell>{violation.violation}</TableCell>
                        <TableCell>{violation.missing_tags?.join(', ')}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </Paper>
      )}
    </Box>
  );
}

export default ReportsView;
