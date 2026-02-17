import React, { useState, useEffect } from 'react';
import {
  Box, Paper, Typography, Grid, Button, TextField, Select, MenuItem, 
  FormControl, InputLabel, Chip, Card, CardContent, CardActions,
  Alert, CircularProgress, Checkbox, FormGroup, FormControlLabel
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { reportAPI, templateAPI } from '../../services/api';

export default function ReportBuilder() {
  const [templates, setTemplates] = useState([]);
  const [reports, setReports] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [reportName, setReportName] = useState('');
  const [outputFormats, setOutputFormats] = useState(['pdf']);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [executions, setExecutions] = useState({});

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [templatesRes, reportsRes] = await Promise.all([
        templateAPI.listTemplates(),
        reportAPI.listReports()
      ]);
      setTemplates(templatesRes.data);
      setReports(reportsRes.data);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load data' });
    }
  };

  const handleFormatChange = (format) => {
    setOutputFormats(prev => 
      prev.includes(format) 
        ? prev.filter(f => f !== format)
        : [...prev, format]
    );
  };

  const handleCreateReport = async () => {
    if (!reportName || !selectedTemplate || outputFormats.length === 0) {
      setMessage({ type: 'error', text: 'Please fill all fields' });
      return;
    }

    setLoading(true);
    try {
      await reportAPI.createReport({
        name: reportName,
        template_id: parseInt(selectedTemplate),
        parameters: { time_range: '7d' },
        output_formats: outputFormats
      });
      
      setMessage({ type: 'success', text: 'Report created successfully' });
      setReportName('');
      setSelectedTemplate('');
      setOutputFormats(['pdf']);
      await loadData();
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to create report' });
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async (reportId) => {
    setLoading(true);
    try {
      await reportAPI.generateReport(reportId);
      setMessage({ type: 'success', text: 'Report generation started' });
      
      // Poll for executions
      setTimeout(async () => {
        const execRes = await reportAPI.getExecutions(reportId);
        setExecutions(prev => ({ ...prev, [reportId]: execRes.data }));
      }, 2000);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to generate report' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      {message && (
        <Alert severity={message.type} onClose={() => setMessage(null)} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Create New Report</Typography>
            
            <TextField
              fullWidth
              label="Report Name"
              value={reportName}
              onChange={(e) => setReportName(e.target.value)}
              margin="normal"
            />
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Template</InputLabel>
              <Select
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
                label="Template"
              >
                {templates.map(t => (
                  <MenuItem key={t.id} value={t.id}>{t.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>Output Formats</Typography>
            <FormGroup row>
              {['pdf', 'excel', 'csv', 'json'].map(format => (
                <FormControlLabel
                  key={format}
                  control={
                    <Checkbox
                      checked={outputFormats.includes(format)}
                      onChange={() => handleFormatChange(format)}
                    />
                  }
                  label={format.toUpperCase()}
                />
              ))}
            </FormGroup>
            
            <Button
              fullWidth
              variant="contained"
              onClick={handleCreateReport}
              disabled={loading}
              sx={{ mt: 2 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Create Report'}
            </Button>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={7}>
          <Typography variant="h6" gutterBottom>Existing Reports</Typography>
          
          <Grid container spacing={2}>
            {reports.map(report => (
              <Grid item xs={12} key={report.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <Typography variant="h6">{report.name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          Template ID: {report.template_id} | State: {report.state}
                        </Typography>
                      </div>
                      <Chip label={report.state} color={report.state === 'COMPLETED' ? 'success' : 'default'} />
                    </Box>
                    
                    {executions[report.id] && executions[report.id].length > 0 && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>Recent Executions:</Typography>
                        {executions[report.id].slice(0, 3).map(exec => (
                          <Box key={exec.id} sx={{ mb: 1, p: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
                            <Typography variant="body2">
                              {exec.state} - {exec.execution_time_ms ? `${exec.execution_time_ms}ms` : 'In progress'}
                            </Typography>
                            {exec.output_paths && (
                              <Box sx={{ mt: 0.5 }}>
                                {Object.keys(exec.output_paths).map(format => (
                                  <Chip key={format} label={format} size="small" sx={{ mr: 0.5 }} />
                                ))}
                              </Box>
                            )}
                          </Box>
                        ))}
                      </Box>
                    )}
                  </CardContent>
                  <CardActions>
                    <Button
                      size="small"
                      startIcon={<PlayArrowIcon />}
                      onClick={() => handleGenerateReport(report.id)}
                      disabled={loading}
                    >
                      Generate
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
}
