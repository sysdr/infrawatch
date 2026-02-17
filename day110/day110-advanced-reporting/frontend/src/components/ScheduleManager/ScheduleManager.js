import React, { useState, useEffect } from 'react';
import {
  Box, Paper, Typography, Grid, Button, TextField, Select, MenuItem,
  FormControl, InputLabel, Card, CardContent, Alert, Chip
} from '@mui/material';
import ScheduleIcon from '@mui/icons-material/Schedule';
import { scheduleAPI, reportAPI } from '../../services/api';

export default function ScheduleManager() {
  const [schedules, setSchedules] = useState([]);
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState('');
  const [cronExpression, setCronExpression] = useState('0 9 * * 1');
  const [message, setMessage] = useState(null);

  const commonCrons = [
    { label: 'Every Monday at 9 AM', value: '0 9 * * 1' },
    { label: 'Daily at 8 AM', value: '0 8 * * *' },
    { label: 'Every Hour', value: '0 * * * *' },
    { label: 'Every 15 minutes', value: '*/15 * * * *' },
  ];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [schedulesRes, reportsRes] = await Promise.all([
        scheduleAPI.listSchedules(),
        reportAPI.listReports()
      ]);
      setSchedules(schedulesRes.data);
      setReports(reportsRes.data);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load data' });
    }
  };

  const handleCreateSchedule = async () => {
    if (!selectedReport || !cronExpression) {
      setMessage({ type: 'error', text: 'Please select report and cron expression' });
      return;
    }

    try {
      await scheduleAPI.createSchedule({
        report_id: parseInt(selectedReport),
        cron_expression: cronExpression,
        timezone: 'UTC'
      });

      setMessage({ type: 'success', text: 'Schedule created' });
      setSelectedReport('');
      await loadData();
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to create schedule' });
    }
  };

  const handleDeleteSchedule = async (id) => {
    try {
      await scheduleAPI.deleteSchedule(id);
      setMessage({ type: 'success', text: 'Schedule deleted' });
      await loadData();
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to delete schedule' });
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
            <Typography variant="h6" gutterBottom>Create Schedule</Typography>
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Report</InputLabel>
              <Select
                value={selectedReport}
                onChange={(e) => setSelectedReport(e.target.value)}
                label="Report"
              >
                {reports.map(r => (
                  <MenuItem key={r.id} value={r.id}>{r.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Frequency</InputLabel>
              <Select
                value={cronExpression}
                onChange={(e) => setCronExpression(e.target.value)}
                label="Frequency"
              >
                {commonCrons.map(cron => (
                  <MenuItem key={cron.value} value={cron.value}>{cron.label}</MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <TextField
              fullWidth
              label="Cron Expression"
              value={cronExpression}
              onChange={(e) => setCronExpression(e.target.value)}
              margin="normal"
              helperText="Custom cron expression (e.g., 0 9 * * 1)"
            />
            
            <Button
              fullWidth
              variant="contained"
              startIcon={<ScheduleIcon />}
              onClick={handleCreateSchedule}
              sx={{ mt: 2 }}
            >
              Create Schedule
            </Button>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={7}>
          <Typography variant="h6" gutterBottom>Active Schedules</Typography>
          
          <Grid container spacing={2}>
            {schedules.map(schedule => (
              <Grid item xs={12} key={schedule.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <Typography variant="h6">Report ID: {schedule.report_id}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          Cron: {schedule.cron_expression}
                        </Typography>
                        <Box sx={{ mt: 1 }}>
                          <Chip 
                            label={schedule.is_active ? 'Active' : 'Inactive'} 
                            color={schedule.is_active ? 'success' : 'default'}
                            size="small"
                            sx={{ mr: 1 }}
                          />
                          <Chip 
                            label={`Timezone: ${schedule.timezone}`} 
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                      </div>
                      <Button
                        color="error"
                        onClick={() => handleDeleteSchedule(schedule.id)}
                      >
                        Delete
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
}
