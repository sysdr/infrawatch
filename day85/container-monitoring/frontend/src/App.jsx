import React, { useState, useEffect } from 'react'
import {
  Box,
  Container,
  AppBar,
  Toolbar,
  Typography,
  Grid,
  Paper,
  Chip,
  Alert,
  CircularProgress,
  Button
} from '@mui/material'
import { Speed as SpeedIcon, Memory as MemoryIcon, Refresh as RefreshIcon } from '@mui/icons-material'
import ContainerList from './components/ContainerList'
import MetricsChart from './components/MetricsChart'
import HealthStatus from './components/HealthStatus'
import EventStream from './components/EventStream'
import AlertPanel from './components/AlertPanel'
import { useWebSocket } from './hooks/useWebSocket'
import { checkBackendHealth } from './utils/healthCheck'

function App() {
  const [containers, setContainers] = useState([])
  const [selectedContainer, setSelectedContainer] = useState(null)
  const [metricsData, setMetricsData] = useState({})
  const [alerts, setAlerts] = useState([])
  const [events, setEvents] = useState([])
  const [backendHealth, setBackendHealth] = useState(null)
  
  // Check backend health on mount
  useEffect(() => {
    const checkHealth = async () => {
      const health = await checkBackendHealth()
      setBackendHealth(health)
    }
    checkHealth()
    const interval = setInterval(checkHealth, 30000) // Check every 30 seconds
    return () => clearInterval(interval)
  }, [])
  
  const { connected, error } = useWebSocket({
    onMetrics: (data) => {
      // Handle empty containers message
      if (data.containers_count === 0 || data.message === "No containers running") {
        // Clear containers list when no containers are running
        setContainers([])
        return
      }
      
      // Handle container metrics update
      if (data.container && data.container.id) {
        // Update containers list
        setContainers(prev => {
          const index = prev.findIndex(c => c.id === data.container.id)
          if (index >= 0) {
            const updated = [...prev]
            updated[index] = {
              ...data.container,
              metrics: data.metrics,
              health: data.health,
              baseline: data.baseline
            }
            return updated
          } else {
            return [...prev, {
              ...data.container,
              metrics: data.metrics,
              health: data.health,
              baseline: data.baseline
            }]
          }
        })
        
        // Update metrics history
        if (data.metrics) {
          setMetricsData(prev => {
            const containerId = data.container.id
            const history = prev[containerId] || []
            return {
              ...prev,
              [containerId]: [...history.slice(-59), data.metrics]
            }
          })
        }
        
        // Update alerts
        if (data.alerts && data.alerts.length > 0) {
          setAlerts(prev => [...prev, ...data.alerts].slice(-100))
        }
      }
    },
    onEvent: (event) => {
      setEvents(prev => [event, ...prev].slice(0, 50))
    }
  })

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <SpeedIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Container Monitoring Dashboard
          </Typography>
          <Chip
            label={connected ? "Connected" : "Disconnected"}
            color={connected ? "success" : "error"}
            size="small"
          />
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {!connected && (
          <Alert 
            severity="warning" 
            sx={{ mb: 2 }}
            action={
              <Button
                color="inherit"
                size="small"
                startIcon={<RefreshIcon />}
                onClick={() => window.location.reload()}
              >
                Retry
              </Button>
            }
          >
            {error || 'Connecting to backend...'}
            {backendHealth && !backendHealth.healthy && (
              <Box sx={{ mt: 1, fontSize: '0.875rem' }}>
                Backend health check failed. Please ensure the backend server is running:
                <br />
                <code>cd backend && source venv/bin/activate && uvicorn backend.app.main:app --reload</code>
              </Box>
            )}
          </Alert>
        )}
        {error && connected && (
          <Alert severity="info" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Container List */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, height: '600px', overflow: 'auto' }}>
              <Typography variant="h6" gutterBottom>
                Containers ({containers.length})
              </Typography>
              <ContainerList
                containers={containers}
                selectedContainer={selectedContainer}
                onSelectContainer={setSelectedContainer}
              />
            </Paper>
          </Grid>

          {/* Metrics Charts */}
          <Grid item xs={12} md={8}>
            {selectedContainer ? (
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>
                      {selectedContainer.name}
                    </Typography>
                    <HealthStatus health={selectedContainer.health} />
                  </Paper>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <MetricsChart
                      title="CPU Usage"
                      data={metricsData[selectedContainer.id] || []}
                      dataKey="cpu_percent"
                      color="#2196f3"
                      unit="%"
                      icon={<SpeedIcon />}
                      baseline={selectedContainer.baseline?.cpu_mean}
                    />
                  </Paper>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <MetricsChart
                      title="Memory Usage"
                      data={metricsData[selectedContainer.id] || []}
                      dataKey="memory_percent"
                      color="#4caf50"
                      unit="%"
                      icon={<MemoryIcon />}
                      baseline={selectedContainer.baseline?.memory_mean}
                    />
                  </Paper>
                </Grid>
              </Grid>
            ) : (
              <Paper sx={{ p: 4, textAlign: 'center', height: '600px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography variant="h6" color="textSecondary">
                  Select a container to view metrics
                </Typography>
              </Paper>
            )}
          </Grid>

          {/* Alerts Panel */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, height: '400px', overflow: 'auto' }}>
              <Typography variant="h6" gutterBottom>
                Active Alerts ({alerts.length})
              </Typography>
              <AlertPanel alerts={alerts} />
            </Paper>
          </Grid>

          {/* Event Stream */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, height: '400px', overflow: 'auto' }}>
              <Typography variant="h6" gutterBottom>
                Event Stream
              </Typography>
              <EventStream events={events} />
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  )
}

export default App
