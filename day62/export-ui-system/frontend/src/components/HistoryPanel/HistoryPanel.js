import React, { useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
} from '@mui/material';
import { Download, Close, StopCircle } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { fetchExports, cancelExport } from '../../redux/exportsSlice';
import formatDistanceToNow from 'date-fns/formatDistanceToNow';

function HistoryPanel() {
  const dispatch = useDispatch();
  const exports = useSelector((state) => state.exports.exports);

  useEffect(() => {
    dispatch(fetchExports('demo-user'));
    const interval = setInterval(() => {
      dispatch(fetchExports('demo-user'));
    }, 5000);
    return () => clearInterval(interval);
  }, [dispatch]);

  const handleCancel = (jobId) => {
    dispatch(cancelExport(jobId));
  };

  const handleDownload = (downloadUrl) => {
    window.open(`http://localhost:8000${downloadUrl}`, '_blank');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'COMPLETED':
        return 'success';
      case 'PROCESSING':
        return 'primary';
      case 'FAILED':
        return 'error';
      case 'CANCELLED':
        return 'default';
      default:
        return 'info';
    }
  };

  const formatBytes = (bytes) => {
    if (!bytes) return '-';
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    return `${(kb / 1024).toFixed(1)} MB`;
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Export History
      </Typography>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Job ID</TableCell>
              <TableCell>Format</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Size</TableCell>
              <TableCell>Rows</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {exports.length === 0 && (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Typography color="text.secondary">No exports yet</Typography>
                </TableCell>
              </TableRow>
            )}
            {exports.map((exportJob) => (
              <TableRow key={exportJob.job_id}>
                <TableCell>{exportJob.job_id.substring(0, 8)}</TableCell>
                <TableCell>{exportJob.format_type}</TableCell>
                <TableCell>
                  <Chip label={exportJob.status} color={getStatusColor(exportJob.status)} size="small" />
                </TableCell>
                <TableCell>{formatBytes(exportJob.file_size)}</TableCell>
                <TableCell>{exportJob.row_count || '-'}</TableCell>
                <TableCell>
                  {formatDistanceToNow(new Date(exportJob.created_at), { addSuffix: true })}
                </TableCell>
                <TableCell>
                  {exportJob.status === 'COMPLETED' && exportJob.download_url && (
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => handleDownload(exportJob.download_url)}
                    >
                      <Download />
                    </IconButton>
                  )}
                  {(exportJob.status === 'PROCESSING' || exportJob.status === 'QUEUED') && (
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleCancel(exportJob.job_id)}
                      title="Cancel export"
                    >
                      <StopCircle />
                    </IconButton>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
}

export default HistoryPanel;
