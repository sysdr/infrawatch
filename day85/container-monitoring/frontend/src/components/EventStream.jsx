import React from 'react'
import { List, ListItem, ListItemText, Chip, Typography } from '@mui/material'
import { format } from 'date-fns'

const getActionColor = (action) => {
  switch (action) {
    case 'start': return 'success'
    case 'stop': case 'die': return 'error'
    case 'restart': return 'warning'
    case 'pause': return 'default'
    default: return 'info'
  }
}

function EventStream({ events }) {
  return (
    <List dense>
      {events.map((event, index) => (
        <ListItem
          key={index}
          sx={{
            mb: 1,
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 1
          }}
        >
          <ListItemText
            primary={
              <>
                <Chip
                  label={event.action}
                  size="small"
                  color={getActionColor(event.action)}
                  sx={{ mr: 1 }}
                />
                {event.container_name}
              </>
            }
            secondary={
              <>
                <Typography variant="caption" display="block">
                  {format(new Date(event.timestamp), 'HH:mm:ss')}
                </Typography>
                {event.exit_code !== null && (
                  <Typography variant="caption" color="error">
                    Exit code: {event.exit_code}
                  </Typography>
                )}
                {event.error && (
                  <Typography variant="caption" color="error" display="block">
                    Error: {event.error}
                  </Typography>
                )}
              </>
            }
          />
        </ListItem>
      ))}
      {events.length === 0 && (
        <Typography variant="body2" color="textSecondary" sx={{ p: 2, textAlign: 'center' }}>
          No events yet
        </Typography>
      )}
    </List>
  )
}

export default EventStream
