import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Grid,
  TextField,
  Button,
  Typography,
  Box,
  Divider,
  Alert,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Switch,
  Select,
  MenuItem,
  InputLabel,
  Card,
  CardContent
} from '@mui/material';
import { Settings, Timeline, Person, Notifications, Dashboard as DashboardIcon } from '@mui/icons-material';
import { preferenceAPI, activityAPI, profileAPI, userAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';

// Default preferences structure matching backend
const DEFAULT_PREFS = {
  theme: "light",
  language: "en",
  timezone: "UTC",
  date_format: "YYYY-MM-DD",
  time_format: "24h",
  notifications: { email: true, push: true, digest_frequency: "daily" },
  dashboard: { default_view: "overview", widgets_per_page: 12, refresh_interval: 30, chart_theme: "default" },
  privacy: { profile_visibility: "team", activity_tracking: true }
};

export default function PreferencesView() {
  const user = useAuthStore((state) => state.user);
  const [preferences, setPreferences] = useState(DEFAULT_PREFS);
  const [formData, setFormData] = useState(DEFAULT_PREFS);
  const [editing, setEditing] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState({
    activityStats: null,
    profile: null,
    userInfo: null
  });

  useEffect(() => {
    loadPreferences();
    loadMetrics();
  }, []);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      const response = await preferenceAPI.getMyPreferences();
      // Ensure we have valid preferences data
      const prefs = response?.data || DEFAULT_PREFS;
      setPreferences(prefs);
      setFormData(prefs);
      setError('');
    } catch (err) {
      console.error('Error loading preferences:', err);
      // Use default preferences if API fails - component already has defaults
      setPreferences(DEFAULT_PREFS);
      setFormData(DEFAULT_PREFS);
      setError('Using default preferences');
    } finally {
      setLoading(false);
    }
  };

  const loadMetrics = async () => {
    try {
      const [activityRes, profileRes, userRes] = await Promise.allSettled([
        activityAPI.getMyActivityStats(30),
        profileAPI.getMyProfile(),
        userAPI.getMe()
      ]);

      setMetrics({
        activityStats: activityRes.status === 'fulfilled' ? activityRes.value.data : null,
        profile: profileRes.status === 'fulfilled' ? profileRes.value.data : null,
        userInfo: userRes.status === 'fulfilled' ? userRes.value.data : null
      });
    } catch (err) {
      console.error('Error loading metrics:', err);
    }
  };

  const calculateProfileCompletion = () => {
    if (!metrics.profile) return 0;
    const fields = ['display_name', 'job_title', 'department', 'location', 'bio', 'avatar_url'];
    const completed = fields.filter(field => {
      const value = metrics.profile[field];
      return value && value.toString().trim() !== '';
    }).length;
    return Math.round((completed / fields.length) * 100);
  };

  const getAccountAge = () => {
    if (!metrics.userInfo || !metrics.userInfo.created_at) return 'N/A';
    const created = new Date(metrics.userInfo.created_at);
    const now = new Date();
    const days = Math.floor((now - created) / (1000 * 60 * 60 * 24));
    if (days < 30) return `${days} days`;
    if (days < 365) return `${Math.floor(days / 30)} months`;
    return `${Math.floor(days / 365)} years`;
  };

  const handleSave = async () => {
    try {
      await preferenceAPI.updateMyPreferences({ preferences: formData });
      setSuccess('Preferences updated successfully');
      setEditing(false);
      loadPreferences();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to update preferences');
      console.error('Error updating preferences:', err);
    }
  };

  const updateNestedPreference = (path, value) => {
    const keys = path.split('.');
    const newData = { ...formData };
    let current = newData;
    
    for (let i = 0; i < keys.length - 1; i++) {
      if (!current[keys[i]]) {
        current[keys[i]] = {};
      }
      current = current[keys[i]];
    }
    
    current[keys[keys.length - 1]] = value;
    setFormData(newData);
  };

  const getNestedValue = (path) => {
    const keys = path.split('.');
    let value = formData;
    for (const key of keys) {
      value = value?.[key];
      if (value === undefined) return '';
    }
    return value;
  };

  // Component always renders - preferences start with defaults
  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Settings sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
          <Typography variant="h4">Preferences</Typography>
        </Box>

        <Divider sx={{ mb: 3 }} />

        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
        {error && <Alert severity="warning" sx={{ mb: 2 }}>{error}</Alert>}
        {loading && <Alert severity="info" sx={{ mb: 2 }}>Loading preferences...</Alert>}

        {/* Metrics Section - Always Show */}
        <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
          Your Metrics
        </Typography>
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'primary.main', color: 'white', height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Timeline sx={{ mr: 1 }} />
                  <Typography variant="h6">Total Activities</Typography>
                </Box>
                <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                  {metrics.activityStats?.total_activities ?? 0}
                </Typography>
                <Typography variant="caption">Last 30 days</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'success.main', color: 'white', height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Person sx={{ mr: 1 }} />
                  <Typography variant="h6">Profile Complete</Typography>
                </Box>
                <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                  {calculateProfileCompletion()}%
                </Typography>
                <Typography variant="caption">Profile information</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'secondary.main', color: 'white', height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Notifications sx={{ mr: 1 }} />
                  <Typography variant="h6">Notifications</Typography>
                </Box>
                <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                  {(() => {
                    const email = preferences?.notifications?.email;
                    const push = preferences?.notifications?.push;
                    if (email && push) return '2';
                    if (email || push) return '1';
                    return '0';
                  })()}
                </Typography>
                <Typography variant="caption">Active channels</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'info.main', color: 'white', height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <DashboardIcon sx={{ mr: 1 }} />
                  <Typography variant="h6">Account Age</Typography>
                </Box>
                <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                  {getAccountAge()}
                </Typography>
                <Typography variant="caption">Member since</Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Activity Breakdown */}
          {metrics.activityStats?.activities_by_type && Object.keys(metrics.activityStats.activities_by_type).length > 0 && (
            <Grid item xs={12}>
              <Paper variant="outlined" sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>Activity Breakdown (Last 30 Days)</Typography>
                <Grid container spacing={2}>
                  {Object.entries(metrics.activityStats.activities_by_type).map(([type, count]) => (
                    <Grid item xs={6} sm={4} md={3} key={type}>
                      <Box sx={{ textAlign: 'center', p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                        <Typography variant="h5" color="primary">{count}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {type.replace('.', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </Typography>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </Grid>
          )}
        </Grid>

        <Divider sx={{ mb: 3 }} />

        <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
          Settings
        </Typography>

        <Grid container spacing={3}>
          {/* Theme Settings */}
          <Grid item xs={12}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Appearance</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth disabled={!editing}>
                    <InputLabel>Theme</InputLabel>
                    <Select
                      value={getNestedValue('theme') || 'light'}
                      onChange={(e) => updateNestedPreference('theme', e.target.value)}
                      label="Theme"
                    >
                      <MenuItem value="light">Light</MenuItem>
                      <MenuItem value="dark">Dark</MenuItem>
                      <MenuItem value="auto">Auto</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth disabled={!editing}>
                    <InputLabel>Language</InputLabel>
                    <Select
                      value={getNestedValue('language') || 'en'}
                      onChange={(e) => updateNestedPreference('language', e.target.value)}
                      label="Language"
                    >
                      <MenuItem value="en">English</MenuItem>
                      <MenuItem value="es">Spanish</MenuItem>
                      <MenuItem value="fr">French</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Timezone"
                    value={getNestedValue('timezone') || 'UTC'}
                    onChange={(e) => updateNestedPreference('timezone', e.target.value)}
                    disabled={!editing}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Date Format"
                    value={getNestedValue('date_format') || 'YYYY-MM-DD'}
                    onChange={(e) => updateNestedPreference('date_format', e.target.value)}
                    disabled={!editing}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth disabled={!editing}>
                    <InputLabel>Time Format</InputLabel>
                    <Select
                      value={getNestedValue('time_format') || '24h'}
                      onChange={(e) => updateNestedPreference('time_format', e.target.value)}
                      label="Time Format"
                    >
                      <MenuItem value="12h">12 Hour</MenuItem>
                      <MenuItem value="24h">24 Hour</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Notifications */}
          <Grid item xs={12}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Notifications</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={getNestedValue('notifications.email') ?? true}
                        onChange={(e) => updateNestedPreference('notifications.email', e.target.checked)}
                        disabled={!editing}
                      />
                    }
                    label="Email Notifications"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={getNestedValue('notifications.push') ?? true}
                        onChange={(e) => updateNestedPreference('notifications.push', e.target.checked)}
                        disabled={!editing}
                      />
                    }
                    label="Push Notifications"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth disabled={!editing}>
                    <InputLabel>Digest Frequency</InputLabel>
                    <Select
                      value={getNestedValue('notifications.digest_frequency') || 'daily'}
                      onChange={(e) => updateNestedPreference('notifications.digest_frequency', e.target.value)}
                      label="Digest Frequency"
                    >
                      <MenuItem value="never">Never</MenuItem>
                      <MenuItem value="daily">Daily</MenuItem>
                      <MenuItem value="weekly">Weekly</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Dashboard Settings */}
          <Grid item xs={12}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Dashboard</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth disabled={!editing}>
                    <InputLabel>Default View</InputLabel>
                    <Select
                      value={getNestedValue('dashboard.default_view') || 'overview'}
                      onChange={(e) => updateNestedPreference('dashboard.default_view', e.target.value)}
                      label="Default View"
                    >
                      <MenuItem value="overview">Overview</MenuItem>
                      <MenuItem value="detailed">Detailed</MenuItem>
                      <MenuItem value="compact">Compact</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Widgets Per Page"
                    value={getNestedValue('dashboard.widgets_per_page') || 12}
                    onChange={(e) => updateNestedPreference('dashboard.widgets_per_page', parseInt(e.target.value))}
                    disabled={!editing}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Refresh Interval (seconds)"
                    value={getNestedValue('dashboard.refresh_interval') || 30}
                    onChange={(e) => updateNestedPreference('dashboard.refresh_interval', parseInt(e.target.value))}
                    disabled={!editing}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth disabled={!editing}>
                    <InputLabel>Chart Theme</InputLabel>
                    <Select
                      value={getNestedValue('dashboard.chart_theme') || 'default'}
                      onChange={(e) => updateNestedPreference('dashboard.chart_theme', e.target.value)}
                      label="Chart Theme"
                    >
                      <MenuItem value="default">Default</MenuItem>
                      <MenuItem value="dark">Dark</MenuItem>
                      <MenuItem value="colorful">Colorful</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Privacy Settings */}
          <Grid item xs={12}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Privacy</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth disabled={!editing}>
                    <InputLabel>Profile Visibility</InputLabel>
                    <Select
                      value={getNestedValue('privacy.profile_visibility') || 'team'}
                      onChange={(e) => updateNestedPreference('privacy.profile_visibility', e.target.value)}
                      label="Profile Visibility"
                    >
                      <MenuItem value="public">Public</MenuItem>
                      <MenuItem value="team">Team</MenuItem>
                      <MenuItem value="private">Private</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={getNestedValue('privacy.activity_tracking') ?? true}
                        onChange={(e) => updateNestedPreference('privacy.activity_tracking', e.target.checked)}
                        disabled={!editing}
                      />
                    }
                    label="Activity Tracking"
                  />
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        </Grid>

        <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
          {editing ? (
            <>
              <Button variant="contained" onClick={handleSave}>
                Save Preferences
              </Button>
              <Button variant="outlined" onClick={() => { setEditing(false); setFormData(preferences); }}>
                Cancel
              </Button>
            </>
          ) : (
            <Button variant="contained" onClick={() => setEditing(true)}>
              Edit Preferences
            </Button>
          )}
        </Box>
      </Paper>
    </Container>
  );
}

