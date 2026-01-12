import React, { useState, useEffect } from 'react'
import {
  Box, Paper, Typography, List, ListItem, ListItemText, Chip, Avatar, ListItemAvatar
} from '@mui/material'
import { format } from 'date-fns'
import { activityAPI } from '../services/api'
import { useWebSocket } from '../contexts/WebSocketContext'

export default function ActivityMonitor() {
  const [activities, setActivities] = useState([])
  const { messages, isConnected } = useWebSocket()

  useEffect(() => {
    loadActivities()
  }, [])

  useEffect(() => {
    // Real-time activity updates
    if (messages.length > 0) {
      loadActivities()
    }
  }, [messages])

  const loadActivities = async () => {
    try {
      const response = await activityAPI.getAll({ limit: 50 })
      setActivities(response.data)
    } catch (error) {
      console.error('Failed to load activities:', error)
    }
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Activity Monitor</Typography>
        <Chip
          label={isConnected ? 'Live' : 'Disconnected'}
          color={isConnected ? 'success' : 'error'}
          size="small"
        />
      </Box>

      <Paper>
        <List>
          {activities.map((activity) => (
            <ListItem key={activity.id}>
              <ListItemAvatar>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  {activity.user_name[0]}
                </Avatar>
              </ListItemAvatar>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body1">{activity.user_name}</Typography>
                    <Chip label={activity.action} size="small" />
                    <Typography variant="body2" color="text.secondary">
                      {activity.resource}
                    </Typography>
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="body2">{activity.details}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {format(new Date(activity.timestamp), 'PPpp')}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  )
}
