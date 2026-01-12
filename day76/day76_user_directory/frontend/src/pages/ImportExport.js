import React, { useState } from 'react';
import {
  Paper, Typography, Box, Button, Alert, LinearProgress,
  FormControlLabel, Switch, Grid
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CloudDownloadIcon from '@mui/icons-material/CloudDownload';
import axios from 'axios';

function ImportExport() {
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState(null);
  const [updateExisting, setUpdateExisting] = useState(false);

  const handleImport = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setImporting(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('update_existing', updateExisting);

    try {
      const response = await axios.post(
        `http://localhost:8000/api/v1/users/import?update_existing=${updateExisting}`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      setResult({ type: 'success', data: response.data });
    } catch (error) {
      setResult({ type: 'error', message: error.message });
    } finally {
      setImporting(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/users/export', {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `users_export_${new Date().toISOString()}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      setResult({ type: 'success', message: 'Export completed successfully' });
    } catch (error) {
      setResult({ type: 'error', message: error.message });
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>User Import/Export</Typography>

      {result && (
        <Alert severity={result.type} sx={{ mb: 3 }} onClose={() => setResult(null)}>
          {result.message || (
            <Box>
              <Typography>Import completed:</Typography>
              <Typography>Total: {result.data?.total_users}</Typography>
              <Typography>Created: {result.data?.created_count}</Typography>
              <Typography>Updated: {result.data?.updated_count}</Typography>
              <Typography>Failed: {result.data?.failed_count}</Typography>
            </Box>
          )}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Import Users</Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              Upload a CSV file with columns: username, email, full_name, department, employee_type, manager
            </Typography>

            <FormControlLabel
              control={
                <Switch
                  checked={updateExisting}
                  onChange={(e) => setUpdateExisting(e.target.checked)}
                />
              }
              label="Update existing users"
            />

            <Box mt={2}>
              <input
                accept=".csv"
                style={{ display: 'none' }}
                id="csv-upload"
                type="file"
                onChange={handleImport}
              />
              <label htmlFor="csv-upload">
                <Button
                  variant="contained"
                  component="span"
                  startIcon={<CloudUploadIcon />}
                  disabled={importing}
                  fullWidth
                >
                  {importing ? 'Importing...' : 'Upload CSV'}
                </Button>
              </label>
            </Box>

            {importing && <LinearProgress sx={{ mt: 2 }} />}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Export Users</Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              Download all users as a CSV file for backup or migration
            </Typography>

            <Button
              variant="contained"
              startIcon={<CloudDownloadIcon />}
              onClick={handleExport}
              fullWidth
            >
              Export to CSV
            </Button>
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>CSV Format Example</Typography>
        <Box component="pre" sx={{ bgcolor: '#f5f5f5', p: 2, borderRadius: 1, overflow: 'auto' }}>
{`username,email,full_name,department,employee_type,manager
jdoe,jdoe@example.com,John Doe,Engineering,Engineer,admin
jsmith,jsmith@example.com,Jane Smith,Sales,Manager,admin`}
        </Box>
      </Paper>
    </Box>
  );
}

export default ImportExport;
