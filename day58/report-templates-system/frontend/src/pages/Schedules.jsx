import React, { useEffect, useState } from 'react';
import { Box, Typography, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem } from '@mui/material';
import { Add, PlayArrow } from '@mui/icons-material';
import { reportApi, templateApi } from '../services/api';

export default function Schedules() {
  const [schedules, setSchedules] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    template_id: '',
    schedule_cron: '0 9 * * MON',
    recipients: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [schedulesRes, templatesRes] = await Promise.all([
        reportApi.getSchedules(),
        templateApi.getAll()
      ]);
      setSchedules(schedulesRes.data);
      setTemplates(templatesRes.data);
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  const handleCreate = async () => {
    try {
      const data = {
        ...formData,
        recipients: formData.recipients.split(',').map(s => s.trim())
      };
      await reportApi.createSchedule(data);
      setOpen(false);
      setFormData({ name: '', template_id: '', schedule_cron: '0 9 * * MON', recipients: '' });
      loadData();
    } catch (error) {
      console.error('Failed to create schedule:', error);
    }
  };

  const handleGenerate = async (scheduleId) => {
    try {
      const response = await reportApi.generate({ scheduled_report_id: scheduleId });
      if (response.data && response.data.execution_id) {
        alert(`Report generation completed! Execution ID: ${response.data.execution_id}`);
        // Reload schedules to update last_run
        loadData();
      } else {
        alert('Report generation started!');
      }
    } catch (error) {
      console.error('Failed to generate report:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to generate report';
      alert(`Error: ${errorMessage}`);
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Scheduled Reports</Typography>
        <Button 
          variant="contained" 
          startIcon={<Add />} 
          onClick={(e) => {
            e.currentTarget.blur();
            setOpen(true);
          }}
        >
          New Schedule
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Schedule</TableCell>
              <TableCell>Recipients</TableCell>
              <TableCell>Last Run</TableCell>
              <TableCell>Next Run</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {schedules.map((schedule) => (
              <TableRow key={schedule.id}>
                <TableCell>{schedule.name}</TableCell>
                <TableCell>{schedule.schedule_cron}</TableCell>
                <TableCell>{schedule.recipients.join(', ')}</TableCell>
                <TableCell>{schedule.last_run ? new Date(schedule.last_run).toLocaleString() : 'Never'}</TableCell>
                <TableCell>{schedule.next_run ? new Date(schedule.next_run).toLocaleString() : 'N/A'}</TableCell>
                <TableCell>
                  <Button
                    size="small"
                    startIcon={<PlayArrow />}
                    onClick={() => handleGenerate(schedule.id)}
                  >
                    Run Now
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog 
        open={open} 
        onClose={() => setOpen(false)} 
        maxWidth="sm" 
        fullWidth
        disableEnforceFocus={false}
        disableAutoFocus={false}
      >
        <DialogTitle>Create Scheduled Report</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            select
            label="Template"
            value={formData.template_id}
            onChange={(e) => setFormData({ ...formData, template_id: e.target.value })}
            margin="normal"
          >
            {templates.map((t) => (
              <MenuItem key={t.id} value={t.id}>{t.name}</MenuItem>
            ))}
          </TextField>
          <TextField
            fullWidth
            label="Schedule (Cron)"
            value={formData.schedule_cron}
            onChange={(e) => setFormData({ ...formData, schedule_cron: e.target.value })}
            margin="normal"
            helperText="e.g., '0 9 * * MON' for Mondays at 9am"
          />
          <TextField
            fullWidth
            label="Recipients (comma-separated)"
            value={formData.recipients}
            onChange={(e) => setFormData({ ...formData, recipients: e.target.value })}
            margin="normal"
            placeholder="user1@example.com, user2@example.com"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleCreate} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
