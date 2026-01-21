import React from 'react'
import { Box, Chip, Typography } from '@mui/material'
import { CheckCircle, Error, Warning, HelpOutline } from '@mui/icons-material'

const getHealthIcon = (status) => {
  switch (status) {
    case 'healthy': return <CheckCircle />
    case 'unhealthy': return <Error />
    case 'starting': return <Warning />
    default: return <HelpOutline />
  }
}

const getHealthColor = (status) => {
  switch (status) {
    case 'healthy': return 'success'
    case 'unhealthy': return 'error'
    case 'starting': return 'warning'
    default: return 'default'
  }
}

function HealthStatus({ health }) {
  if (!health) {
    return (
      <Chip label="No health check" size="small" icon={<HelpOutline />} />
    )
  }

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Chip
        label={`Health: ${health.status}`}
        color={getHealthColor(health.status)}
        icon={getHealthIcon(health.status)}
        size="small"
      />
      {health.failing_streak > 0 && (
        <Chip
          label={`Failures: ${health.failing_streak}`}
          color="error"
          size="small"
        />
      )}
      {health.log && (
        <Typography variant="caption" color="textSecondary" sx={{ ml: 1 }}>
          {health.log.substring(0, 100)}
        </Typography>
      )}
    </Box>
  )
}

export default HealthStatus
