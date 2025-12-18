import React from 'react'
import { Container, Box, Typography } from '@mui/material'
import InteractiveDashboard from './components/InteractiveDashboard'

function App() {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f5', py: 4 }}>
      <Container maxWidth="xl">
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 600, mb: 4 }}>
          Interactive Dashboard System
        </Typography>
        <InteractiveDashboard />
      </Container>
    </Box>
  )
}

export default App
