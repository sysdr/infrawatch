import React, { useState } from 'react';
import {
  Paper, Typography, TextField, Button, Box, Alert, Card, CardContent,
  Grid, Chip, CircularProgress
} from '@mui/material';
import { createOrganization, createRole, createTeam, getTeamDashboard } from '../../services/api';

// Helper to get API base URL dynamically
const getApiBase = () => {
  if (typeof window === 'undefined') {
    return 'http://localhost:8000';
  }
  const hostname = window.location.hostname;
  if (hostname && hostname !== 'localhost' && hostname !== '127.0.0.1' && !hostname.includes('localhost')) {
    return `http://${hostname}:8000`;
  }
  return 'http://localhost:8000';
};

function TeamCreation({ onTeamCreated }) {
  const [orgId, setOrgId] = useState(null);
  const [roleId, setRoleId] = useState(null);
  const [teamName, setTeamName] = useState('');
  const [teamDesc, setTeamDesc] = useState('');
  const [message, setMessage] = useState(null);
  const [createdTeams, setCreatedTeams] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loadingMetrics, setLoadingMetrics] = useState(false);
  const [isCreatingOrg, setIsCreatingOrg] = useState(false);
  const [isCreatingRole, setIsCreatingRole] = useState(false);
  const [isCreatingTeam, setIsCreatingTeam] = useState(false);

  const handleCreateOrg = async () => {
    // Prevent multiple simultaneous requests
    if (isCreatingOrg || orgId !== null) {
      return;
    }
    
    setIsCreatingOrg(true);
    setMessage(null);
    setMessage({ type: 'info', text: 'Creating organization...' });
    
    try {
      // Test backend connection first
      try {
        const apiBase = getApiBase();
        const healthCheck = await fetch(`${apiBase}/health`);
        if (!healthCheck.ok) {
          throw new Error('Backend health check failed');
        }
      } catch (healthError) {
        const apiBase = getApiBase();
        setMessage({ 
          type: 'error', 
          text: `Cannot connect to backend server. Please ensure the backend is running on ${apiBase}. Check console for details.` 
        });
        console.error('Backend connection test failed:', healthError);
        return;
      }
      
      // Generate unique slug with timestamp
      const timestamp = Date.now();
      const randomSuffix = Math.floor(Math.random() * 10000);
      const uniqueSlug = `demo-org-${timestamp}-${randomSuffix}`;
      
      console.log('Creating organization with slug:', uniqueSlug);
      console.log('Request payload:', { name: 'Demo Organization', slug: uniqueSlug, settings: {} });
      
      const org = await createOrganization({
        name: 'Demo Organization',
        slug: uniqueSlug,
        settings: {}
      });
      
      console.log('Organization created successfully:', org);
      setOrgId(org.id);
      setMessage({ type: 'success', text: `Organization created: ${org.name} (ID: ${org.id})` });
      setIsCreatingOrg(false);
    } catch (error) {
      console.error('Organization creation error - Full error object:', error);
      console.error('Error response:', error.response);
      console.error('Error request:', error.request);
      console.error('Error message:', error.message);
      console.error('Error code:', error.code);
      
      let errorMsg = 'Failed to create organization';
      
      if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error') || error.message?.includes('ERR_CONNECTION_REFUSED') || error.message?.includes('Failed to fetch')) {
        const apiBase = getApiBase();
        errorMsg = `Cannot connect to backend server. Please ensure the backend is running on ${apiBase}`;
      } else if (error.response) {
        // Server responded with error
        const status = error.response.status;
        const data = error.response.data;
        
        console.log('Error Response Status:', status);
        console.log('Error Response Data:', data);
        
        if (status === 400) {
          // Handle 400 Bad Request
          if (Array.isArray(data?.detail)) {
            // Validation errors
            errorMsg = data.detail.map(err => {
              const field = err.loc?.slice(1).join('.') || 'field';
              return `${field}: ${err.msg}`;
            }).join(', ');
          } else if (data?.detail) {
            // Single error message
            errorMsg = data.detail;
          } else {
            errorMsg = 'Bad request. Please check the organization name and slug.';
          }
        } else if (status === 500) {
          errorMsg = data?.detail || data?.message || 'Server error occurred';
        } else {
          errorMsg = data?.detail || data?.message || `Error ${status}: ${error.response.statusText}`;
        }
      } else if (error.request) {
        // Request made but no response
        const apiBase = getApiBase();
        errorMsg = `No response from server. Check if backend is running on ${apiBase}`;
      } else {
        errorMsg = error.message || 'Unknown error occurred';
      }
      
      setMessage({ type: 'error', text: errorMsg });
      setIsCreatingOrg(false);
    }
  };

  const handleCreateRole = async () => {
    // Prevent multiple simultaneous requests
    if (isCreatingRole || roleId !== null || !orgId) {
      return;
    }
    
    setIsCreatingRole(true);
    try {
      // Generate unique role name with timestamp
      const timestamp = Date.now();
      const role = await createRole({
        name: `Member-${timestamp}`,
        description: 'Team member role',
        permissions: ['read', 'write']
      });
      setRoleId(role.id);
      setMessage({ type: 'success', text: `Role created: ${role.name} (ID: ${role.id})` });
      setIsCreatingRole(false);
    } catch (error) {
      console.error('Role creation error:', error);
      let errorMsg = 'Failed to create role';
      
      if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error') || error.message?.includes('ERR_CONNECTION_REFUSED') || error.message?.includes('Failed to fetch')) {
        const apiBase = getApiBase();
        errorMsg = `Cannot connect to backend server. Please ensure the backend is running on ${apiBase}`;
      } else if (error.response) {
        errorMsg = error.response?.data?.detail || error.message || 'Failed to create role';
      } else {
        errorMsg = error.message || 'Failed to create role';
      }
      
      setMessage({ type: 'error', text: `Failed to create role: ${errorMsg}` });
      setIsCreatingRole(false);
    }
  };

  const handleCreateTeam = async () => {
    if (!orgId) {
      setMessage({ type: 'error', text: 'Create organization first' });
      return;
    }
    
    // Prevent multiple simultaneous requests
    if (isCreatingTeam || !teamName.trim()) {
      return;
    }
    
    setIsCreatingTeam(true);
    try {
      const team = await createTeam({
        organization_id: orgId,
        name: teamName,
        description: teamDesc,
        parent_team_id: null,
        metadata: {}
      });
      
      setCreatedTeams([...createdTeams, team]);
      setMessage({ type: 'success', text: `Team created: ${team.name}` });
      onTeamCreated(team.id);
      
      // Load and display metrics
      await loadTeamMetrics(team.id);
      
      setTeamName('');
      setTeamDesc('');
      setIsCreatingTeam(false);
    } catch (error) {
      console.error('Team creation error:', error);
      let errorMsg = 'Failed to create team';
      
      if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error') || error.message?.includes('ERR_CONNECTION_REFUSED') || error.message?.includes('Failed to fetch')) {
        const apiBase = getApiBase();
        errorMsg = `Cannot connect to backend server. Please ensure the backend is running on ${apiBase}`;
      } else if (error.response) {
        // Server responded with error
        const status = error.response.status;
        const data = error.response.data;
        
        if (status === 400) {
          if (Array.isArray(data?.detail)) {
            errorMsg = data.detail.map(err => {
              const field = err.loc?.slice(1).join('.') || 'field';
              return `${field}: ${err.msg}`;
            }).join(', ');
          } else if (data?.detail) {
            errorMsg = data.detail;
          } else {
            errorMsg = 'Bad request. Please check the team name and description.';
          }
        } else if (status === 500) {
          errorMsg = data?.detail || data?.message || 'Server error occurred';
        } else {
          errorMsg = data?.detail || data?.message || `Error ${status}: ${error.response.statusText}`;
        }
      } else if (error.request) {
        const apiBase = getApiBase();
        errorMsg = `No response from server. Check if backend is running on ${apiBase}`;
      } else {
        errorMsg = error.message || 'Unknown error occurred';
      }
      
      setMessage({ type: 'error', text: `Failed to create team: ${errorMsg}` });
      setIsCreatingTeam(false);
    }
  };

  const loadTeamMetrics = async (teamId) => {
    setLoadingMetrics(true);
    try {
      const dashboardData = await getTeamDashboard(teamId);
      setMetrics(dashboardData);
    } catch (error) {
      console.error('Failed to load metrics:', error);
      setMessage({ type: 'error', text: 'Team created but failed to load metrics' });
    } finally {
      setLoadingMetrics(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>Team Management System</Typography>
      
      {message && (
        <Alert severity={message.type} onClose={() => setMessage(null)} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>1. Setup Organization</Typography>
              <Button 
                variant="contained" 
                onClick={handleCreateOrg}
                disabled={orgId !== null || isCreatingOrg}
                fullWidth
              >
                {isCreatingOrg ? 'Creating...' : orgId ? `Org Created (ID: ${orgId})` : 'Create Organization'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>2. Setup Role</Typography>
              <Button 
                variant="contained" 
                onClick={handleCreateRole}
                disabled={!orgId || roleId !== null || isCreatingRole}
                fullWidth
              >
                {isCreatingRole ? 'Creating...' : roleId ? `Role Created (ID: ${roleId})` : 'Create Member Role'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>3. Create Team</Typography>
              <TextField
                label="Team Name"
                value={teamName}
                onChange={(e) => setTeamName(e.target.value)}
                fullWidth
                margin="normal"
                size="small"
                disabled={!orgId}
              />
              <TextField
                label="Description"
                value={teamDesc}
                onChange={(e) => setTeamDesc(e.target.value)}
                fullWidth
                margin="normal"
                size="small"
                multiline
                rows={2}
                disabled={!orgId}
              />
              <Button 
                variant="contained" 
                onClick={handleCreateTeam}
                disabled={!orgId || !teamName || isCreatingTeam}
                fullWidth
                sx={{ mt: 1 }}
              >
                {isCreatingTeam ? 'Creating...' : 'Create Team'}
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {createdTeams.length > 0 && (
        <Paper sx={{ p: 2, mt: 3 }}>
          <Typography variant="h6" gutterBottom>Created Teams</Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {createdTeams.map(team => (
              <Chip 
                key={team.id}
                label={`${team.name} (ID: ${team.id})`}
                color="primary"
                onClick={() => {
                  onTeamCreated(team.id);
                  loadTeamMetrics(team.id);
                }}
              />
            ))}
          </Box>
        </Paper>
      )}

      {loadingMetrics && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <CircularProgress />
          <Typography sx={{ ml: 2 }}>Loading metrics...</Typography>
        </Box>
      )}

      {metrics && !loadingMetrics && (
        <Paper sx={{ p: 3, mt: 3, bgcolor: 'background.default' }}>
          <Typography variant="h5" gutterBottom color="primary">
            Team Metrics: {metrics.team_name}
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>Total Members</Typography>
                  <Typography variant="h4" color="primary">{metrics.total_members}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>Active Today</Typography>
                  <Typography variant="h4" color="success.main">{metrics.active_members_today}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>Active This Week</Typography>
                  <Typography variant="h4" color="info.main">{metrics.active_members_week}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>Total Activities</Typography>
                  <Typography variant="h4" color="secondary">{metrics.total_activities}</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
          {metrics.recent_activities && metrics.recent_activities.length > 0 && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>Recent Activities</Typography>
              <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
                {metrics.recent_activities.slice(0, 5).map((activity, idx) => (
                  <Box key={activity.id || idx} sx={{ mb: 1, p: 1, bgcolor: 'action.hover', borderRadius: 1 }}>
                    <Typography variant="body2" fontWeight="bold">
                      {activity.type?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {activity.description} • {new Date(activity.created_at).toLocaleString()}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Box>
          )}
        </Paper>
      )}
    </Box>
  );
}

export default TeamCreation;
