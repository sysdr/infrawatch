import React, { useState } from 'react';
import {
    ThemeProvider, createTheme, CssBaseline, Container, AppBar, Toolbar,
    Typography, Box, Button, Dialog, DialogTitle, DialogContent, DialogActions,
    TextField, Select, MenuItem, FormControl, InputLabel, Grid
} from '@mui/material';
import { CloudUpload } from '@mui/icons-material';
import ExportJobList from './components/ExportJobList';
import ExportSchedule from './components/ExportSchedule';
import StatsDashboard from './components/StatsDashboard';
import { exportAPI } from './services/api';

const theme = createTheme({
    palette: {
        mode: 'light',
        primary: { main: '#1976d2' },
        secondary: { main: '#dc004e' },
    },
});

function App() {
    const [openDialog, setOpenDialog] = useState(false);
    const [formData, setFormData] = useState({
        export_type: 'metrics',
        format: 'csv'
    });

    const handleCreateExport = async () => {
        try {
            await exportAPI.createExport(formData);
            setOpenDialog(false);
            window.location.reload();
        } catch (error) {
            console.error('Failed to create export:', error);
        }
    };

    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <AppBar position="static" elevation={2}>
                <Toolbar>
                    <CloudUpload sx={{ mr: 2 }} />
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                        Export Integration System
                    </Typography>
                    <Button color="inherit" onClick={() => setOpenDialog(true)}>
                        New Export
                    </Button>
                </Toolbar>
            </AppBar>

            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Grid container spacing={3}>
                    <Grid item xs={12}>
                        <StatsDashboard />
                    </Grid>
                    <Grid item xs={12}>
                        <ExportJobList />
                    </Grid>
                    <Grid item xs={12}>
                        <ExportSchedule />
                    </Grid>
                </Grid>
            </Container>

            <Dialog 
                open={openDialog} 
                onClose={() => setOpenDialog(false)} 
                maxWidth="sm" 
                fullWidth
                disableEnforceFocus
            >
                <DialogTitle>Create New Export</DialogTitle>
                <DialogContent>
                    <FormControl fullWidth margin="normal">
                        <InputLabel>Export Type</InputLabel>
                        <Select
                            value={formData.export_type}
                            onChange={(e) => setFormData({ ...formData, export_type: e.target.value })}
                        >
                            <MenuItem value="metrics">Metrics Data</MenuItem>
                            <MenuItem value="alerts">Alert History</MenuItem>
                            <MenuItem value="logs">System Logs</MenuItem>
                        </Select>
                    </FormControl>

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
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
                    <Button onClick={handleCreateExport} variant="contained">Create Export</Button>
                </DialogActions>
            </Dialog>
        </ThemeProvider>
    );
}

export default App;
