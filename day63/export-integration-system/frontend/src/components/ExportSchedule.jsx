import React, { useState, useEffect } from 'react';
import {
    Paper, Box, Typography, Button, Dialog, DialogTitle, DialogContent,
    DialogActions, TextField, Select, MenuItem, FormControl, InputLabel,
    List, ListItem, ListItemText, ListItemSecondaryAction, IconButton, Chip
} from '@mui/material';
import { Add, Delete, Schedule } from '@mui/icons-material';
import { exportAPI } from '../services/api';

const ExportSchedule = () => {
    const [schedules, setSchedules] = useState([]);
    const [openDialog, setOpenDialog] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        export_type: 'metrics',
        format: 'csv',
        schedule_expression: '0 9 * * *', // Daily at 9 AM
        email_recipients: []
    });

    const loadSchedules = async () => {
        try {
            const response = await exportAPI.listSchedules();
            setSchedules(response.data);
        } catch (error) {
            console.error('Failed to load schedules:', error);
        }
    };

    useEffect(() => {
        loadSchedules();
    }, []);

    const handleSubmit = async () => {
        try {
            await exportAPI.createSchedule(formData);
            setOpenDialog(false);
            setFormData({
                name: '',
                export_type: 'metrics',
                format: 'csv',
                schedule_expression: '0 9 * * *',
                email_recipients: []
            });
            loadSchedules();
        } catch (error) {
            console.error('Failed to create schedule:', error);
        }
    };

    const handleDelete = async (scheduleId) => {
        try {
            await exportAPI.deleteSchedule(scheduleId);
            loadSchedules();
        } catch (error) {
            console.error('Failed to delete schedule:', error);
        }
    };

    return (
        <Paper elevation={3} sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h5">Scheduled Exports</Typography>
                <Button
                    startIcon={<Add />}
                    variant="contained"
                    onClick={() => setOpenDialog(true)}
                >
                    New Schedule
                </Button>
            </Box>

            <List>
                {schedules.map((schedule) => (
                    <ListItem key={schedule.id} divider>
                        <Schedule sx={{ mr: 2 }} />
                        <ListItemText
                            primary={schedule.name}
                            secondaryTypographyProps={{ component: 'div' }}
                            secondary={
                                <div>
                                    <div style={{ fontSize: '0.875rem', color: 'rgba(0, 0, 0, 0.6)', marginBottom: '4px' }}>
                                        {schedule.schedule_expression} • {schedule.format.toUpperCase()}
                                    </div>
                                    <div style={{ display: 'inline-flex', alignItems: 'center', marginTop: '4px' }}>
                                        <Chip
                                            label={schedule.enabled ? 'Active' : 'Disabled'}
                                            color={schedule.enabled ? 'success' : 'default'}
                                            size="small"
                                        />
                                        <span style={{ fontSize: '0.75rem', marginLeft: '8px', color: 'rgba(0, 0, 0, 0.6)' }}>
                                            Runs: {schedule.run_count}
                                        </span>
                                    </div>
                                </div>
                            }
                        />
                        <ListItemSecondaryAction>
                            <IconButton edge="end" onClick={() => handleDelete(schedule.id)}>
                                <Delete />
                            </IconButton>
                        </ListItemSecondaryAction>
                    </ListItem>
                ))}
            </List>

            {schedules.length === 0 && (
                <Box textAlign="center" py={4}>
                    <Typography color="text.secondary">No scheduled exports configured</Typography>
                </Box>
            )}

            <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Create Scheduled Export</DialogTitle>
                <DialogContent>
                    <TextField
                        label="Schedule Name"
                        fullWidth
                        margin="normal"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    />

                    <FormControl fullWidth margin="normal">
                        <InputLabel>Format</InputLabel>
                        <Select
                            value={formData.format}
                            onChange={(e) => setFormData({ ...formData, format: e.target.value })}
                        >
                            <MenuItem value="csv">CSV</MenuItem>
                            <MenuItem value="json">JSON</MenuItem>
                            <MenuItem value="excel">Excel</MenuItem>
                        </Select>
                    </FormControl>

                    <TextField
                        label="Cron Expression"
                        fullWidth
                        margin="normal"
                        value={formData.schedule_expression}
                        onChange={(e) => setFormData({ ...formData, schedule_expression: e.target.value })}
                        helperText="e.g., '0 9 * * *' for daily at 9 AM"
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
                    <Button onClick={handleSubmit} variant="contained">Create</Button>
                </DialogActions>
            </Dialog>
        </Paper>
    );
};

export default ExportSchedule;
