import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const MetricsPage = () => {
  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Metrics Management
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Manage metric categories, retention policies, and aggregation rules
        </Typography>
      </Box>
    </Container>
  );
};

export default MetricsPage;
