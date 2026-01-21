import React from 'react'
import {
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Chip,
  Box,
  Typography
} from '@mui/material'
import { CheckCircle, Error, Warning, Pause } from '@mui/icons-material'

const getStatusColor = (status) => {
  switch (status) {
    case 'running': return 'success'
    case 'exited': return 'error'
    case 'paused': return 'warning'
    default: return 'default'
  }
}

const getStatusIcon = (status) => {
  switch (status) {
    case 'running': return <CheckCircle color="success" />
    case 'exited': return <Error color="error" />
    case 'paused': return <Pause color="warning" />
    default: return <Warning color="action" />
  }
}

function ContainerList({ containers, selectedContainer, onSelectContainer }) {
  return (
    <List>
      {containers.map((container) => {
        const isSelected = selectedContainer?.id === container.id
        const metrics = container.metrics
        
        return (
          <ListItem
            key={container.id}
            disablePadding
            sx={{
              mb: 1,
              border: '1px solid',
              borderColor: isSelected ? 'primary.main' : 'divider',
              borderRadius: 1
            }}
          >
            <ListItemButton
              selected={isSelected}
              onClick={() => onSelectContainer(container)}
            >
              <ListItemIcon>
                {getStatusIcon(container.status)}
              </ListItemIcon>
              <ListItemText
                primary={container.name}
                secondaryTypographyProps={{ component: 'div' }}
                secondary={
                  <Box>
                    <Typography variant="caption" component="div" display="block">
                      {container.image}
                    </Typography>
                    {metrics && (
                      <Box sx={{ mt: 0.5 }}>
                        <Chip
                          label={`CPU: ${metrics.cpu_percent.toFixed(1)}%`}
                          size="small"
                          color={metrics.cpu_percent > 80 ? 'error' : 'default'}
                          sx={{ mr: 0.5, fontSize: '0.7rem' }}
                        />
                        <Chip
                          label={`Mem: ${metrics.memory_percent.toFixed(1)}%`}
                          size="small"
                          color={metrics.memory_percent > 80 ? 'error' : 'default'}
                          sx={{ fontSize: '0.7rem' }}
                        />
                      </Box>
                    )}
                  </Box>
                }
              />
              <Chip
                label={container.status}
                color={getStatusColor(container.status)}
                size="small"
              />
            </ListItemButton>
          </ListItem>
        )
      })}
      {containers.length === 0 && (
        <Typography variant="body2" color="textSecondary" sx={{ p: 2, textAlign: 'center' }}>
          No containers running
        </Typography>
      )}
    </List>
  )
}

export default ContainerList
