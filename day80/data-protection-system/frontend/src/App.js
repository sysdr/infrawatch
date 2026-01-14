import React, { useState, useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Container,
  AppBar,
  Toolbar,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  Tabs,
  Tab,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress
} from '@mui/material';
import {
  Lock,
  Security,
  Shield,
  Visibility,
  CheckCircle,
  Error as ErrorIcon
} from '@mui/icons-material';
import axios from 'axios';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#388e3c',
    },
  },
});

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [currentTab, setCurrentTab] = useState(0);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState(null);

  // Encryption state
  const [plaintext, setPlaintext] = useState('');
  const [encryptedData, setEncryptedData] = useState(null);
  const [decryptedText, setDecryptedText] = useState('');

  // Masking state
  const [maskingText, setMaskingText] = useState('');
  const [maskedResult, setMaskedResult] = useState('');

  // Privacy state
  const [userId, setUserId] = useState(1);
  const [consents, setConsents] = useState({});
  const [auditLogs, setAuditLogs] = useState([]);

  // GDPR state
  const [gdprUserId, setGdprUserId] = useState(1);
  const [gdprRequests, setGdprRequests] = useState([]);

  useEffect(() => {
    loadMetrics();
    loadConsents();
    loadAuditLogs();
  }, []);

  const loadMetrics = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/metrics`);
      setMetrics(response.data);
    } catch (error) {
      console.error('Error loading metrics:', error);
    }
  };

  const loadConsents = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/privacy/user-consents/${userId}`);
      setConsents(response.data.consents);
    } catch (error) {
      console.error('Error loading consents:', error);
    }
  };

  const loadAuditLogs = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/privacy/audit-logs/${userId}`);
      setAuditLogs(response.data.logs);
    } catch (error) {
      console.error('Error loading audit logs:', error);
    }
  };

  const handleEncrypt = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/encryption/encrypt`, {
        plaintext: plaintext,
        context: 'dashboard'
      });
      setEncryptedData(response.data.encrypted_data);
      setAlert({ type: 'success', message: 'Data encrypted successfully' });
    } catch (error) {
      setAlert({ type: 'error', message: 'Encryption failed: ' + error.message });
    }
    setLoading(false);
  };

  const handleDecrypt = async () => {
    if (!encryptedData) {
      setAlert({ type: 'error', message: 'No encrypted data to decrypt' });
      return;
    }
    
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/encryption/decrypt`, {
        encrypted_data: encryptedData
      });
      setDecryptedText(response.data.plaintext);
      setAlert({ type: 'success', message: 'Data decrypted successfully' });
    } catch (error) {
      setAlert({ type: 'error', message: 'Decryption failed: ' + error.message });
    }
    setLoading(false);
  };

  const handleMaskText = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/masking/mask-text`, {
        text: maskingText
      });
      setMaskedResult(response.data.masked_text);
      setAlert({ type: 'success', message: 'Text masked successfully' });
    } catch (error) {
      setAlert({ type: 'error', message: 'Masking failed: ' + error.message });
    }
    setLoading(false);
  };

  const handleGrantConsent = async (purpose) => {
    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/api/privacy/grant-consent`, {
        user_id: userId,
        purposes: [purpose]
      });
      await loadConsents();
      setAlert({ type: 'success', message: `Consent granted for ${purpose}` });
    } catch (error) {
      setAlert({ type: 'error', message: 'Failed to grant consent: ' + error.message });
    }
    setLoading(false);
  };

  const handleRevokeConsent = async (purpose) => {
    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/api/privacy/revoke-consent`, {
        user_id: userId,
        purposes: [purpose]
      });
      await loadConsents();
      setAlert({ type: 'success', message: `Consent revoked for ${purpose}` });
    } catch (error) {
      setAlert({ type: 'error', message: 'Failed to revoke consent: ' + error.message });
    }
    setLoading(false);
  };

  const handleGDPRRequest = async (requestType) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/gdpr/${requestType}-request`, {
        user_id: gdprUserId
      });
      setAlert({ type: 'success', message: `${requestType} request created: ${response.data.request_id}` });
      setGdprRequests([...gdprRequests, response.data]);
    } catch (error) {
      setAlert({ type: 'error', message: `Failed to create ${requestType} request: ` + error.message });
    }
    setLoading(false);
  };

  const classificationData = [
    { name: 'Public', value: 12000, color: '#4caf50' },
    { name: 'Internal', value: 20000, color: '#2196f3' },
    { name: 'Confidential', value: 10000, color: '#ff9800' },
    { name: 'Restricted', value: 3230, color: '#f44336' }
  ];

  const encryptionPerformanceData = [
    { time: '00:00', operations: 1200 },
    { time: '04:00', operations: 980 },
    { time: '08:00', operations: 1450 },
    { time: '12:00', operations: 1800 },
    { time: '16:00', operations: 2100 },
    { time: '20:00', operations: 1600 }
  ];

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Shield sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Data Protection System Dashboard
            </Typography>
            <Chip label="Enterprise Edition" color="secondary" />
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          {alert && (
            <Alert severity={alert.type} onClose={() => setAlert(null)} sx={{ mb: 2 }}>
              {alert.message}
            </Alert>
          )}

          {loading && <LinearProgress sx={{ mb: 2 }} />}

          {/* Metrics Overview */}
          {metrics && (
            <Grid container spacing={3} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      <Lock fontSize="small" /> Active Keys
                    </Typography>
                    <Typography variant="h4">
                      {metrics.encryption.keys_active}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {metrics.encryption.encryption_operations_per_sec} ops/sec
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      <Security fontSize="small" /> Classified Records
                    </Typography>
                    <Typography variant="h4">
                      {metrics.classification.classified_records.toLocaleString()}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {metrics.classification.restricted} restricted
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      <CheckCircle fontSize="small" /> Active Consents
                    </Typography>
                    <Typography variant="h4">
                      {metrics.privacy.active_consents.toLocaleString()}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {metrics.privacy.consent_checks_per_sec} checks/sec
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      <Visibility fontSize="small" /> GDPR Requests
                    </Typography>
                    <Typography variant="h4">
                      {metrics.gdpr.pending_requests}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {metrics.gdpr.avg_completion_hours}h avg
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}

          {/* Charts */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Data Classification Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={classificationData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      label
                    >
                      {classificationData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Encryption Operations (24h)
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={encryptionPerformanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Area
                      type="monotone"
                      dataKey="operations"
                      stroke="#1976d2"
                      fill="#1976d2"
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
          </Grid>

          {/* Main Tabs */}
          <Paper sx={{ width: '100%' }}>
            <Tabs value={currentTab} onChange={(e, v) => setCurrentTab(v)} centered>
              <Tab label="Encryption" icon={<Lock />} />
              <Tab label="Data Masking" icon={<Visibility />} />
              <Tab label="Privacy & Consent" icon={<Security />} />
              <Tab label="GDPR Compliance" icon={<Shield />} />
            </Tabs>

            <Box sx={{ p: 3 }}>
              {/* Encryption Tab */}
              {currentTab === 0 && (
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" gutterBottom>
                      Encrypt Data (AES-256-GCM)
                    </Typography>
                    <TextField
                      fullWidth
                      multiline
                      rows={4}
                      label="Plaintext"
                      value={plaintext}
                      onChange={(e) => setPlaintext(e.target.value)}
                      sx={{ mb: 2 }}
                    />
                    <Button
                      variant="contained"
                      onClick={handleEncrypt}
                      disabled={!plaintext || loading}
                      fullWidth
                    >
                      Encrypt
                    </Button>
                    {encryptedData && (
                      <Paper sx={{ p: 2, mt: 2, bgcolor: '#f5f5f5' }}>
                        <Typography variant="caption" display="block">
                          Ciphertext (truncated):
                        </Typography>
                        <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                          {encryptedData.ciphertext.substring(0, 100)}...
                        </Typography>
                        <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                          Version: {encryptedData.version} | Context: {encryptedData.context}
                        </Typography>
                      </Paper>
                    )}
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" gutterBottom>
                      Decrypt Data
                    </Typography>
                    <Button
                      variant="contained"
                      onClick={handleDecrypt}
                      disabled={!encryptedData || loading}
                      fullWidth
                      color="secondary"
                    >
                      Decrypt
                    </Button>
                    {decryptedText && (
                      <Paper sx={{ p: 2, mt: 2, bgcolor: '#e8f5e9' }}>
                        <Typography variant="caption" display="block">
                          Decrypted plaintext:
                        </Typography>
                        <Typography variant="body1">
                          {decryptedText}
                        </Typography>
                      </Paper>
                    )}
                  </Grid>
                </Grid>
              )}

              {/* Masking Tab */}
              {currentTab === 1 && (
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Typography variant="h6" gutterBottom>
                      Automatic PII Detection & Masking
                    </Typography>
                    <TextField
                      fullWidth
                      multiline
                      rows={4}
                      label="Text with PII"
                      placeholder="Enter text containing emails, phones, SSNs, credit cards..."
                      value={maskingText}
                      onChange={(e) => setMaskingText(e.target.value)}
                      sx={{ mb: 2 }}
                    />
                    <Button
                      variant="contained"
                      onClick={handleMaskText}
                      disabled={!maskingText || loading}
                    >
                      Mask PII
                    </Button>
                    {maskedResult && (
                      <Paper sx={{ p: 2, mt: 2, bgcolor: '#fff3e0' }}>
                        <Typography variant="caption" display="block">
                          Masked text:
                        </Typography>
                        <Typography variant="body1">
                          {maskedResult}
                        </Typography>
                      </Paper>
                    )}
                  </Grid>
                </Grid>
              )}

              {/* Privacy & Consent Tab */}
              {currentTab === 2 && (
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" gutterBottom>
                      Consent Management (User ID: {userId})
                    </Typography>
                    <Box sx={{ mb: 3 }}>
                      {Object.entries(consents).map(([purpose, granted]) => (
                        <Box key={purpose} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <Chip
                            label={purpose}
                            color={granted ? 'success' : 'default'}
                            icon={granted ? <CheckCircle /> : <ErrorIcon />}
                            sx={{ mr: 1, minWidth: 200 }}
                          />
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => granted ? handleRevokeConsent(purpose) : handleGrantConsent(purpose)}
                          >
                            {granted ? 'Revoke' : 'Grant'}
                          </Button>
                        </Box>
                      ))}
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" gutterBottom>
                      Recent Audit Logs
                    </Typography>
                    <TableContainer>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Action</TableCell>
                            <TableCell>Resource</TableCell>
                            <TableCell>Purpose</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {auditLogs.slice(0, 5).map((log) => (
                            <TableRow key={log.id}>
                              <TableCell>{log.action}</TableCell>
                              <TableCell>{log.resource}</TableCell>
                              <TableCell>{log.purpose}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Grid>
                </Grid>
              )}

              {/* GDPR Tab */}
              {currentTab === 3 && (
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" gutterBottom>
                      GDPR Request Management
                    </Typography>
                    <TextField
                      fullWidth
                      type="number"
                      label="User ID"
                      value={gdprUserId}
                      onChange={(e) => setGdprUserId(parseInt(e.target.value))}
                      sx={{ mb: 2 }}
                    />
                    <Box sx={{ display: 'flex', gap: 1, flexDirection: 'column' }}>
                      <Button
                        variant="contained"
                        onClick={() => handleGDPRRequest('access')}
                        disabled={loading}
                      >
                        Request Data Access
                      </Button>
                      <Button
                        variant="contained"
                        onClick={() => handleGDPRRequest('portability')}
                        disabled={loading}
                        color="secondary"
                      >
                        Request Data Portability
                      </Button>
                      <Button
                        variant="contained"
                        onClick={() => handleGDPRRequest('erasure')}
                        disabled={loading}
                        color="error"
                      >
                        Request Data Erasure
                      </Button>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" gutterBottom>
                      Recent GDPR Requests
                    </Typography>
                    {gdprRequests.length === 0 ? (
                      <Typography color="textSecondary">
                        No requests yet
                      </Typography>
                    ) : (
                      <TableContainer>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Request ID</TableCell>
                              <TableCell>Status</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {gdprRequests.map((req) => (
                              <TableRow key={req.request_id}>
                                <TableCell>{req.request_id}</TableCell>
                                <TableCell>
                                  <Chip label={req.status} size="small" />
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    )}
                  </Grid>
                </Grid>
              )}
            </Box>
          </Paper>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
