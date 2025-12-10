import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Button,
} from '@mui/material';
import { useDispatch } from 'react-redux';
import { updateExportProgress } from '../../redux/exportsSlice';
import websocketService from '../../services/websocket';

function ProgressTracker({ jobId, status, progress = 0, downloadUrl }) {
  const dispatch = useDispatch();
  const [currentStage, setCurrentStage] = useState('');

  useEffect(() => {
    if (status === 'PROCESSING' || status === 'QUEUED') {
      websocketService.connect();
      websocketService.subscribe(jobId, (data) => {
        dispatch(updateExportProgress(data));
        if (data.stage) setCurrentStage(data.stage);
      });

      return () => {
        websocketService.unsubscribe(jobId);
      };
    }
  }, [jobId, status, dispatch]);

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

  const handleDownload = () => {
    window.open(`http://localhost:8000${downloadUrl}`, '_blank');
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Export {jobId.substring(0, 8)}</Typography>
          <Chip label={status} color={getStatusColor(status)} />
        </Box>

        {(status === 'PROCESSING' || status === 'QUEUED') && (
          <>
            <LinearProgress variant="determinate" value={progress} sx={{ mb: 1 }} />
            <Typography variant="body2" color="text.secondary">
              {Math.round(progress)}% - {currentStage || 'Starting...'}
            </Typography>
          </>
        )}

        {status === 'COMPLETED' && downloadUrl && (
          <Button variant="contained" fullWidth onClick={handleDownload}>
            Download Export
          </Button>
        )}

        {status === 'FAILED' && (
          <Typography color="error" variant="body2">
            Export failed. Please try again.
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

export default ProgressTracker;
