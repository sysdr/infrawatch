import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { AppBar, Toolbar, Typography, Container, Box, Drawer, List, ListItem, ListItemText, ListItemIcon } from '@mui/material'
import PeopleIcon from '@mui/icons-material/People'
import GroupsIcon from '@mui/icons-material/Groups'
import SecurityIcon from '@mui/icons-material/Security'
import PersonIcon from '@mui/icons-material/Person'
import TimelineIcon from '@mui/icons-material/Timeline'

import UserManagement from './pages/UserManagement'
import TeamManagement from './pages/TeamManagement'
import PermissionManagement from './pages/PermissionManagement'
import UserProfile from './pages/UserProfile'
import ActivityMonitor from './pages/ActivityMonitor'
import Dashboard from './pages/Dashboard'
import { WebSocketProvider } from './contexts/WebSocketContext'
import DashboardIcon from '@mui/icons-material/Dashboard'

const drawerWidth = 240

function App() {
  return (
    <WebSocketProvider>
      <Router>
        <Box sx={{ display: 'flex' }}>
          <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
            <Toolbar>
              <Typography variant="h6" noWrap component="div">
                User Management System
              </Typography>
            </Toolbar>
          </AppBar>
          
          <Drawer
            variant="permanent"
            sx={{
              width: drawerWidth,
              flexShrink: 0,
              '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box' },
            }}
          >
            <Toolbar />
            <Box sx={{ overflow: 'auto' }}>
              <List>
                <ListItem component={Link} to="/dashboard">
                  <ListItemIcon><DashboardIcon /></ListItemIcon>
                  <ListItemText primary="Dashboard" />
                </ListItem>
                <ListItem component={Link} to="/users">
                  <ListItemIcon><PeopleIcon /></ListItemIcon>
                  <ListItemText primary="Users" />
                </ListItem>
                <ListItem component={Link} to="/teams">
                  <ListItemIcon><GroupsIcon /></ListItemIcon>
                  <ListItemText primary="Teams" />
                </ListItem>
                <ListItem component={Link} to="/permissions">
                  <ListItemIcon><SecurityIcon /></ListItemIcon>
                  <ListItemText primary="Permissions" />
                </ListItem>
                <ListItem component={Link} to="/profile/1">
                  <ListItemIcon><PersonIcon /></ListItemIcon>
                  <ListItemText primary="Profile" />
                </ListItem>
                <ListItem component={Link} to="/activity">
                  <ListItemIcon><TimelineIcon /></ListItemIcon>
                  <ListItemText primary="Activity" />
                </ListItem>
              </List>
            </Box>
          </Drawer>
          
          <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
            <Toolbar />
            <Container maxWidth="xl">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/users" element={<UserManagement />} />
                <Route path="/teams" element={<TeamManagement />} />
                <Route path="/permissions" element={<PermissionManagement />} />
                <Route path="/profile/:userId" element={<UserProfile />} />
                <Route path="/activity" element={<ActivityMonitor />} />
              </Routes>
            </Container>
          </Box>
        </Box>
      </Router>
    </WebSocketProvider>
  )
}

export default App
