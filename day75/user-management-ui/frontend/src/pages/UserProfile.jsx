import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  Box, Paper, Typography, Avatar, Grid, Card, CardContent, Chip,
  List, ListItem, ListItemText, Divider
} from '@mui/material'
import { format } from 'date-fns'
import { userAPI, activityAPI } from '../services/api'

export default function UserProfile() {
  const { userId } = useParams()
  const [user, setUser] = useState(null)
  const [activities, setActivities] = useState([])

  useEffect(() => {
    loadProfile()
  }, [userId])

  const loadProfile = async () => {
    try {
      const [userRes, activityRes] = await Promise.all([
        userAPI.getById(userId),
        activityAPI.getAll({ user_id: userId, limit: 20 })
      ])
      setUser(userRes.data)
      setActivities(activityRes.data)
    } catch (error) {
      console.error('Failed to load profile:', error)
    }
  }

  if (!user) return <Typography>Loading...</Typography>

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3 }}>User Profile</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Avatar
              src={user.avatar}
              alt={user.name}
              sx={{ width: 120, height: 120, mx: 'auto', mb: 2 }}
            />
            <Typography variant="h5">{user.name}</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {user.email}
            </Typography>
            <Chip
              label={user.status}
              color={user.status === 'active' ? 'success' : 'default'}
              sx={{ mb: 2 }}
            />
            <Divider sx={{ my: 2 }} />
            <Box sx={{ textAlign: 'left' }}>
              <Typography variant="subtitle2" gutterBottom>Roles</Typography>
              <Box sx={{ mb: 2 }}>
                {user.roles.map((role) => (
                  <Chip key={role} label={role} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                ))}
              </Box>
              <Typography variant="subtitle2" gutterBottom>Teams</Typography>
              <Box>
                {user.teams.map((team) => (
                  <Chip key={team} label={team} size="small" variant="outlined" sx={{ mr: 0.5, mb: 0.5 }} />
                ))}
              </Box>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Recent Activity</Typography>
            <List>
              {activities.map((activity) => (
                <React.Fragment key={activity.id}>
                  <ListItem>
                    <ListItemText
                      primary={`${activity.action} ${activity.resource}`}
                      secondary={
                        <>
                          <Typography variant="body2" component="span">
                            {activity.details}
                          </Typography>
                          <br />
                          <Typography variant="caption" color="text.secondary">
                            {format(new Date(activity.timestamp), 'PPpp')}
                          </Typography>
                        </>
                      }
                    />
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}
