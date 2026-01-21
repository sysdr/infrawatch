import React from 'react'
import { List, ListItem, ListItemText, Chip, Box, Typography } from '@mui/material'
import { Warning, Error } from '@mui/icons-material'
import { format } from 'date-fns'

function AlertPanel({ alerts }) {
  const sortedAlerts = [...alerts].sort(
    (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
  )

  return (
    <List dense>
      {sortedAlerts.map((alert, index) => (
        <ListItem
          key={index}
          sx={{
            mb: 1,
            border: '1px solid',
            borderColor: alert.severity === 'critical' ? 'error.main' : 'warning.main',
            borderRadius: 1,
            bgcolor: alert.severity === 'critical' ? 'error.light' : 'warning.light',
            opacity: 0.9
          }}
        >
          <ListItemText
            primary={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {alert.severity === 'critical' ? (
                  <Error color="error" fontSize="small" />
                ) : (
                  <Warning color="warning" fontSize="small" />
                )}
                <Typography variant="body2" fontWeight="bold">
                  {alert.container_name}
                </Typography>
                <Chip
                  label={alert.severity}
                  size="small"
                  color={alert.severity === 'critical' ? 'error' : 'warning'}
                />
              </Box>
            }
            secondary={
              <>
                <Typography variant="body2">{alert.message}</Typography>
                <Typography variant="caption" color="textSecondary">
                  {format(new Date(alert.timestamp), 'HH:mm:ss')}
                </Typography>
              </>
            }
          />
        </ListItem>
      ))}
      {alerts.length === 0 && (
        <Typography variant="body2" color="textSecondary" sx={{ p: 2, textAlign: 'center' }}>
          No active alerts
        </Typography>
      )}
    </List>
  )
}

export default AlertPanel
