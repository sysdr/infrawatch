import React, { useState, useEffect } from 'react';
import {
    Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    Chip, Button, Box, Typography, LinearProgress, IconButton, Tooltip
} from '@mui/material';
import { Download, Refresh, CheckCircle, Error, HourglassEmpty } from '@mui/icons-material';
import { exportAPI } from '../services/api';
import { formatDistanceToNow } from 'date-fns';

const ExportJobList = () => {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);

    const loadJobs = async () => {
        try {
            setLoading(true);
            const response = await exportAPI.listExports();
            setJobs(response.data);
        } catch (error) {
            console.error('Failed to load jobs:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadJobs();
        const interval = setInterval(loadJobs, 10000); // Poll every 10 seconds
        return () => clearInterval(interval);
    }, []);

    const getStatusIcon = (status) => {
        switch (status) {
            case 'completed':
                return <CheckCircle color="success" />;
            case 'failed':
                return <Error color="error" />;
            case 'processing':
                return <HourglassEmpty color="info" />;
            default:
                return <HourglassEmpty color="disabled" />;
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'completed': return 'success';
            case 'failed': return 'error';
            case 'processing': return 'info';
            default: return 'default';
        }
    };

    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    };

    return (
        <Paper elevation={3} sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h5">Export Jobs</Typography>
                <IconButton onClick={loadJobs} color="primary">
                    <Refresh />
                </IconButton>
            </Box>

            {loading && <LinearProgress sx={{ mb: 2 }} />}

            <TableContainer>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Status</TableCell>
                            <TableCell>Type</TableCell>
                            <TableCell>Format</TableCell>
                            <TableCell>Rows</TableCell>
                            <TableCell>Size</TableCell>
                            <TableCell>Created</TableCell>
                            <TableCell>Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {jobs.map((job) => (
                            <TableRow key={job.id} hover>
                                <TableCell>
                                    <Box display="flex" alignItems="center" gap={1}>
                                        {getStatusIcon(job.status)}
                                        <Chip
                                            label={job.status}
                                            color={getStatusColor(job.status)}
                                            size="small"
                                        />
                                    </Box>
                                </TableCell>
                                <TableCell>{job.export_type}</TableCell>
                                <TableCell>
                                    <Chip label={job.format.toUpperCase()} size="small" variant="outlined" />
                                </TableCell>
                                <TableCell>{job.row_count.toLocaleString()}</TableCell>
                                <TableCell>{formatFileSize(job.file_size)}</TableCell>
                                <TableCell>
                                    <Tooltip title={new Date(job.created_at).toLocaleString()}>
                                        <span>{formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}</span>
                                    </Tooltip>
                                </TableCell>
                                <TableCell>
                                    {job.status === 'completed' && (
                                        <Button
                                            startIcon={<Download />}
                                            variant="contained"
                                            size="small"
                                            href={exportAPI.downloadExport(job.id)}
                                            target="_blank"
                                        >
                                            Download
                                        </Button>
                                    )}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>

            {jobs.length === 0 && !loading && (
                <Box textAlign="center" py={4}>
                    <Typography color="text.secondary">No export jobs found</Typography>
                </Box>
            )}
        </Paper>
    );
};

export default ExportJobList;
