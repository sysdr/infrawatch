import React from 'react';
import { AppBar, Toolbar, Typography } from '@mui/material';

const Navbar = () => (
  <AppBar position="static" color="inherit" elevation={1}>
    <Toolbar>
      <Typography variant="h6">Server Management</Typography>
    </Toolbar>
  </AppBar>
);

export default Navbar;
