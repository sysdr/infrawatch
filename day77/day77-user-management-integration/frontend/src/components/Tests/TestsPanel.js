import React, { useState, useEffect } from 'react';
import {
  Paper, Box, Typography, Button, LinearProgress, Grid, Card, CardContent,
  List, ListItem, ListItemText, Chip
} from '@mui/material';
import { testAPI } from '../../services/api';
import toast from 'react-hot-toast';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';

function TestsPanel() {
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState(null);
  const [progress, setProgress] = useState(0);

  const runTests = async () => {
    try {
      setRunning(true);
      setProgress(0);
      const response = await testAPI.runTests();
      const testId = response.data.test_id;
      
      toast.success('Tests started');
      
      // Poll for results
      const pollInterval = setInterval(async () => {
        try {
          const resultResponse = await testAPI.getResults(testId);
          const data = resultResponse.data;
          
          if (data.tests) {
            setResults(data);
            setProgress((data.tests.length / 5) * 100);
          }
          
          if (data.status === 'completed') {
            clearInterval(pollInterval);
            setRunning(false);
            setProgress(100);
            toast.success('Tests completed');
          }
        } catch (error) {
          console.error('Error polling results:', error);
        }
      }, 2000);
      
      // Stop polling after 2 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        setRunning(false);
      }, 120000);
      
    } catch (error) {
      toast.error('Error running tests');
      setRunning(false);
    }
  };

  const getStatusIcon = (status) => {
    return status === 'passed' ? (
      <CheckCircleIcon sx={{ color: 'success.main' }} />
    ) : (
      <ErrorIcon sx={{ color: 'error.main' }} />
    );
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Integration Tests</Typography>
        <Button
          variant="contained"
          startIcon={<PlayArrowIcon />}
          onClick={runTests}
          disabled={running}
          size="large"
        >
          Run Tests
        </Button>
      </Box>

      {running && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Running Tests...
          </Typography>
          <LinearProgress variant="determinate" value={progress} />
          <Typography variant="body2" sx={{ mt: 1 }}>
            Progress: {Math.round(progress)}%
          </Typography>
        </Paper>
      )}

      {results && (
        <Box>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Total Tests
                  </Typography>
                  <Typography variant="h4">
                    {results.tests?.length || 0}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Passed
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {results.tests?.filter(t => t.status === 'passed').length || 0}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Failed
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    {results.tests?.filter(t => t.status === 'failed').length || 0}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Test Results
                </Typography>
                <List>
                  {results.tests?.map((test, index) => (
                    <ListItem key={index}>
                      <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                        {getStatusIcon(test.status)}
                        <Box sx={{ ml: 2, flexGrow: 1 }}>
                          <ListItemText
                            primary={test.name}
                            secondary={test.details || test.error}
                          />
                        </Box>
                        <Chip
                          label={`${test.duration}ms`}
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Grid>
          </Grid>
        </Box>
      )}

      {!running && !results && (
        <Paper sx={{ p: 6, textAlign: 'center' }}>
          <Typography variant="h6" color="textSecondary" gutterBottom>
            No test results yet
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Click "Run Tests" to start the integration test suite
          </Typography>
        </Paper>
      )}
    </Box>
  );
}

export default TestsPanel;
