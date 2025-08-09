import React from 'react';
import { useParams } from 'react-router-dom';
import { Box, Typography } from '@mui/material';

const ServerDetailPage = () => {
  const { serverId } = useParams();
  return (
    <Box>
      <Typography variant="h4">Server Details</Typography>
      <Typography variant="body1">ID: {serverId}</Typography>
    </Box>
  );
};

export default ServerDetailPage;
