import React, { useState, useEffect } from 'react'
import {
  Box, Paper, Typography, Grid, Card, CardContent, Chip,
  LinearProgress, CircularProgress
} from '@mui/material'
import PeopleIcon from '@mui/icons-material/People'
import GroupsIcon from '@mui/icons-material/Groups'
import SecurityIcon from '@mui/icons-material/Security'
import TimelineIcon from '@mui/icons-material/Timeline'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import { userAPI, teamAPI, roleAPI, activityAPI } from '../services/api'
import { useWebSocket } from '../contexts/WebSocketContext'

export default function Dashboard() {
  const [metrics, setMetrics] = useState({
    totalUsers: 0,
    activeUsers: 0,
    inactiveUsers: 0,
    totalTeams: 0,
    totalRoles: 0,
    totalActivities: 0,
    loading: true
  })
  const { messages, isConnected } = useWebSocket()

  useEffect(() => {
    loadMetrics()
  }, [])

  useEffect(() => {
    // Refresh metrics when WebSocket messages arrive
    if (messages.length > 0) {
      loadMetrics()
    }
  }, [messages])

  const loadMetrics = async () => {
    try {
      const [usersRes, teamsRes, rolesRes, activitiesRes] = await Promise.all([
        userAPI.getAll({}),
        teamAPI.getAll(),
        roleAPI.getAll(),
        activityAPI.getAll({ limit: 1000 })
      ])

      const users = usersRes.data
      const activeUsers = users.filter(u => u.status === 'active').length
      const inactiveUsers = users.filter(u => u.status === 'inactive').length

      setMetrics({
        totalUsers: users.length,
        activeUsers,
        inactiveUsers,
        totalTeams: teamsRes.data.length,
        totalRoles: rolesRes.data.length,
        totalActivities: activitiesRes.data.length,
        loading: false
      })
    } catch (error) {
      console.error('Failed to load metrics:', error)
      setMetrics(prev => ({ ...prev, loading: false }))
    }
  }

  if (metrics.loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <CircularProgress />
      </Box>
    )
  }

  const metricCards = [
    {
      title: 'Total Users',
      value: metrics.totalUsers,
      icon: <PeopleIcon sx={{ fontSize: 40 }} />,
      color: '#1976d2',
      subtitle: `${metrics.activeUsers} active, ${metrics.inactiveUsers} inactive`
    },
    {
      title: 'Active Users',
      value: metrics.activeUsers,
      icon: <CheckCircleIcon sx={{ fontSize: 40 }} />,
      color: '#2e7d32',
      subtitle: `${metrics.totalUsers > 0 ? Math.round((metrics.activeUsers / metrics.totalUsers) * 100) : 0}% of total`
    },
    {
      title: 'Teams',
      value: metrics.totalTeams,
      icon: <GroupsIcon sx={{ fontSize: 40 }} />,
      color: '#ed6c02',
      subtitle: 'Total teams'
    },
    {
      title: 'Roles',
      value: metrics.totalRoles,
      icon: <SecurityIcon sx={{ fontSize: 40 }} />,
      color: '#9c27b0',
      subtitle: 'Total roles'
    },
    {
      title: 'Activities',
      value: metrics.totalActivities,
      icon: <TimelineIcon sx={{ fontSize: 40 }} />,
      color: '#d32f2f',
      subtitle: 'Total activities logged'
    }
  ]

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Dashboard</Typography>
        <Chip
          label={isConnected ? 'Live Updates' : 'Disconnected'}
          color={isConnected ? 'success' : 'error'}
          size="small"
        />
      </Box>

      <Grid container spacing={3}>
        {metricCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box>
                    <Typography color="text.secondary" gutterBottom variant="h6">
                      {card.title}
                    </Typography>
                    <Typography variant="h3" component="div" sx={{ fontWeight: 'bold', color: card.color }}>
                      {card.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {card.subtitle}
                    </Typography>
                  </Box>
                  <Box sx={{ color: card.color, opacity: 0.7 }}>
                    {card.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Paper sx={{ mt: 3, p: 3 }}>
        <Typography variant="h6" gutterBottom>System Status</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">WebSocket Connection</Typography>
            <Chip
              label={isConnected ? 'Connected' : 'Disconnected'}
              color={isConnected ? 'success' : 'error'}
              size="small"
              sx={{ mt: 1 }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">Data Freshness</Typography>
            <Typography variant="body1" sx={{ mt: 1 }}>
              Last updated: {new Date().toLocaleTimeString()}
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  )
}
