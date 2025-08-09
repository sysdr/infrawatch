import React, { useRef, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  LinearProgress
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function ServerDashboard() {
  const [tabValue, setTabValue] = useState(0);
  const [searchFilters, setSearchFilters] = useState({
    filters: [],
    page: 1,
    page_size: 20
  });
  const [bulkDialog, setBulkDialog] = useState(false);
  const [selectedRows, setSelectedRows] = useState([]);
  const [rowSelectionModel, setRowSelectionModel] = useState([]);
  const [bulkAction, setBulkAction] = useState('');

  // Create Group dialog state
  const [groupDialogOpen, setGroupDialogOpen] = useState(false);
  const [groupForm, setGroupForm] = useState({
    name: '',
    description: '',
    color: '#3B82F6'
  });

  // Create Template dialog state
  const [templateDialogOpen, setTemplateDialogOpen] = useState(false);
  const [templateForm, setTemplateForm] = useState({
    name: '',
    description: '',
    configText: '{\n  "instance_type": "t3.micro",\n  "region": "us-east-1",\n  "cpu_cores": 2,\n  "memory_gb": 4\n}'
  });

  // Import/Export
  const fileInputRef = useRef(null);
  const [exportLoading, setExportLoading] = useState(false);
  
  const queryClient = useQueryClient();

  // Fetch servers with search/filter
  const { data: serversData, isLoading: serversLoading } = useQuery(
    ['servers', searchFilters],
    () => api.post('/servers/search', searchFilters).then(res => res.data),
    { enabled: true }
  );

  // Fetch groups
  const { data: groups } = useQuery(
    'groups',
    () => api.get('/server-groups').then(res => res.data)
  );

  // Fetch templates
  const { data: templates } = useQuery(
    'templates',
    () => api.get('/templates').then(res => res.data)
  );

  const [bulkTaskIds, setBulkTaskIds] = useState(() => {
    try {
      const saved = localStorage.getItem('bulkTaskIds');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  React.useEffect(() => {
    try {
      localStorage.setItem('bulkTaskIds', JSON.stringify(bulkTaskIds.slice(0, 20)));
    } catch {}
  }, [bulkTaskIds]);

  // Bulk action mutation
  const bulkMutation = useMutation(
    (actionData) => api.post('/servers/bulk-action', actionData),
    {
      onSuccess: (res) => {
        const taskId = res?.data?.task_id;
        if (taskId) {
          setBulkTaskIds((prev) => [taskId, ...prev.filter((id) => id !== taskId)].slice(0, 20));
        }
        queryClient.invalidateQueries('servers');
        setBulkDialog(false);
        setSelectedRows([]);
      }
    }
  );

  // Create group mutation
  const createGroupMutation = useMutation(
    (payload) => api.post('/server-groups', payload).then(res => res.data),
    {
      onSuccess: () => {
        setGroupDialogOpen(false);
        setGroupForm({ name: '', description: '', color: '#3B82F6' });
        queryClient.invalidateQueries('groups');
      }
    }
  );

  // Create template mutation
  const createTemplateMutation = useMutation(
    (payload) => api.post('/templates', payload).then(res => res.data),
    {
      onSuccess: () => {
        setTemplateDialogOpen(false);
        setTemplateForm({ name: '', description: '', configText: '' });
        queryClient.invalidateQueries('templates');
      }
    }
  );

  // Import servers mutation
  const importServersMutation = useMutation(
    (file) => {
      const formData = new FormData();
      formData.append('file', file);
      return api.post('/servers/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      }).then(res => res.data);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('servers');
      }
    }
  );

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleBulkAction = () => {
    if (!bulkAction || selectedRows.length === 0) return;
    
    bulkMutation.mutate({
      action: bulkAction,
      server_ids: selectedRows,
      parameters: {}
    });
  };

  const handleExport = async () => {
    try {
      setExportLoading(true);
      const response = await api.get('/servers/export', {
        params: { format: 'csv' },
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'servers_export.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } finally {
      setExportLoading(false);
    }
  };

  const handleImportClick = () => fileInputRef.current?.click();
  const handleImportChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      importServersMutation.mutate(file);
      e.target.value = '';
    }
  };

  const handleCreateGroup = () => {
    if (!groupForm.name.trim()) return;
    createGroupMutation.mutate({
      name: groupForm.name,
      description: groupForm.description,
      color: groupForm.color
    });
  };

  const handleCreateTemplate = () => {
    if (!templateForm.name.trim()) return;
    let config;
    try {
      config = JSON.parse(templateForm.configText || '{}');
    } catch (e) {
      alert('Config must be valid JSON');
      return;
    }
    createTemplateMutation.mutate({
      name: templateForm.name,
      description: templateForm.description,
      config,
      version: '1.0.0'
    });
  };

  const serverColumns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'name', headerName: 'Name', width: 150 },
    { field: 'hostname', headerName: 'Hostname', width: 180 },
    { field: 'ip_address', headerName: 'IP Address', width: 130 },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          color={
            params.value === 'running' ? 'success' :
            params.value === 'stopped' ? 'error' : 'default'
          }
          size="small"
        />
      )
    },
    { field: 'region', headerName: 'Region', width: 120 },
    { field: 'instance_type', headerName: 'Type', width: 100 },
    { field: 'cpu_cores', headerName: 'CPU', width: 80 },
    { field: 'memory_gb', headerName: 'Memory (GB)', width: 110 },
    { field: 'os_type', headerName: 'OS', width: 120 },
  ];

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ color: '#23282d', fontWeight: 600 }}>
        Server Management
      </Typography>

      <Paper sx={{ width: '100%', bgcolor: 'white', borderRadius: 2, boxShadow: 1 }}>
        <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Servers" />
          <Tab label="Groups" />
          <Tab label="Templates" />
          <Tab label="Bulk Operations" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Box sx={{ mb: 2 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  placeholder="Search servers..."
                  variant="outlined"
                  size="small"
                  onChange={(e) => {
                    const value = e.target.value;
                    setSearchFilters(prev => ({
                      ...prev,
                      filters: value ? [{ field: 'name', operator: 'like', value }] : []
                    }));
                  }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="contained"
                    disabled={selectedRows.length === 0}
                    onClick={() => setBulkDialog(true)}
                  >
                    Bulk Actions ({selectedRows.length})
                  </Button>
                  <Button variant="outlined" onClick={handleExport} disabled={exportLoading}>
                    {exportLoading ? 'Exporting…' : 'Export'}
                  </Button>
                  <Button variant="outlined" onClick={handleImportClick} disabled={importServersMutation.isLoading}>
                    {importServersMutation.isLoading ? 'Importing…' : 'Import'}
                  </Button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                    style={{ display: 'none' }}
                    onChange={handleImportChange}
                  />
                </Box>
              </Grid>
            </Grid>
          </Box>

          <Box sx={{ height: 600, width: '100%' }}>
            <DataGrid
              rows={serversData?.servers || []}
              columns={serverColumns}
              pageSize={20}
              rowsPerPageOptions={[20, 50, 100]}
              checkboxSelection
              loading={serversLoading}
              rowSelectionModel={rowSelectionModel}
              onRowSelectionModelChange={(newSelection) => {
                setRowSelectionModel(newSelection);
                setSelectedRows(newSelection);
              }}
              sx={{
                '& .MuiDataGrid-root': {
                  border: 'none',
                },
                '& .MuiDataGrid-cell': {
                  borderBottom: '1px solid #e0e0e0',
                },
                '& .MuiDataGrid-columnHeaders': {
                  backgroundColor: '#f8f9fa',
                  borderBottom: '2px solid #e0e0e0',
                },
              }}
            />
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box sx={{ mb: 2 }}>
            <Button variant="contained" onClick={() => setGroupDialogOpen(true)}>Create Group</Button>
          </Box>
          <Grid container spacing={3}>
            {groups?.map((group) => (
              <Grid item xs={12} md={6} lg={4} key={group.id}>
                <Card sx={{ borderLeft: `4px solid ${group.color}` }}>
                  <CardContent>
                    <Typography variant="h6">{group.name}</Typography>
                    <Typography color="text.secondary" gutterBottom>
                      {group.description}
                    </Typography>
                    <Typography variant="body2">
                      {group.server_count} servers
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Box sx={{ mb: 2 }}>
            <Button variant="contained" onClick={() => setTemplateDialogOpen(true)}>Create Template</Button>
          </Box>
          <Grid container spacing={3}>
            {templates?.map((template) => (
              <Grid item xs={12} md={6} lg={4} key={template.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">{template.name}</Typography>
                    <Typography color="text.secondary" gutterBottom>
                      {template.description}
                    </Typography>
                    <Typography variant="body2">
                      Version: {template.version}
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      <Button size="small">Deploy</Button>
                      <Button size="small">Edit</Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Alert severity="info" sx={{ mb: 2 }}>
            Select servers from the Servers tab and choose bulk actions here.
          </Alert>
          {bulkMutation.isLoading && (
            <Box sx={{ mb: 2 }}>
              <LinearProgress />
              <Typography variant="body2" sx={{ mt: 1 }}>
                Processing bulk action...
              </Typography>
            </Box>
          )}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {bulkTaskIds.length === 0 && (
              <Typography color="text.secondary">No bulk tasks yet.</Typography>
            )}
            {bulkTaskIds.map((taskId) => (
              <BulkTaskStatus key={taskId} taskId={taskId} />
            ))}
          </Box>
        </TabPanel>
      </Paper>

      {/* Create Group Dialog */}
      <Dialog open={groupDialogOpen} onClose={() => setGroupDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Group</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Name"
              value={groupForm.name}
              onChange={(e) => setGroupForm({ ...groupForm, name: e.target.value })}
              fullWidth
            />
            <TextField
              label="Description"
              value={groupForm.description}
              onChange={(e) => setGroupForm({ ...groupForm, description: e.target.value })}
              fullWidth
            />
            <TextField
              label="Color"
              value={groupForm.color}
              onChange={(e) => setGroupForm({ ...groupForm, color: e.target.value })}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setGroupDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateGroup} variant="contained" disabled={createGroupMutation.isLoading}>
            {createGroupMutation.isLoading ? 'Creating…' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Template Dialog */}
      <Dialog open={templateDialogOpen} onClose={() => setTemplateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Template</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Name"
              value={templateForm.name}
              onChange={(e) => setTemplateForm({ ...templateForm, name: e.target.value })}
              fullWidth
            />
            <TextField
              label="Description"
              value={templateForm.description}
              onChange={(e) => setTemplateForm({ ...templateForm, description: e.target.value })}
              fullWidth
            />
            <TextField
              label="Config (JSON)"
              value={templateForm.configText}
              onChange={(e) => setTemplateForm({ ...templateForm, configText: e.target.value })}
              fullWidth
              multiline
              minRows={6}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTemplateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateTemplate} variant="contained" disabled={createTemplateMutation.isLoading}>
            {createTemplateMutation.isLoading ? 'Creating…' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Bulk Action Dialog */}
      <Dialog open={bulkDialog} onClose={() => setBulkDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Bulk Action</DialogTitle>
        <DialogContent>
          <Typography gutterBottom>
            Perform action on {selectedRows.length} selected servers
          </Typography>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Action</InputLabel>
            <Select
              value={bulkAction}
              onChange={(e) => setBulkAction(e.target.value)}
              label="Action"
            >
              <MenuItem value="start">Start</MenuItem>
              <MenuItem value="stop">Stop</MenuItem>
              <MenuItem value="restart">Restart</MenuItem>
              <MenuItem value="delete">Delete</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBulkDialog(false)}>Cancel</Button>
          <Button
            onClick={handleBulkAction}
            variant="contained"
            disabled={!bulkAction || bulkMutation.isLoading}
          >
            Execute
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ServerDashboard;

function BulkTaskStatus({ taskId }) {
  const fetchStatus = () => api.get(`/bulk-tasks/${taskId}`).then((r) => r.data);
  const { data, isLoading } = useQuery(['bulkTask', taskId], fetchStatus, {
    refetchInterval: (data) => {
      if (!data) return 1000;
      return data.status === 'completed' || data.status === 'error' ? false : 1000;
    },
    refetchOnWindowFocus: false,
  });

  const percent = React.useMemo(() => {
    if (!data || !data.total) return 0;
    const p = Math.round((Number(data.progress || 0) / Number(data.total || 1)) * 100);
    return isNaN(p) ? 0 : p;
  }, [data]);

  return (
    <Paper sx={{ p: 2, borderRadius: 2 }} variant="outlined">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle1">Task {taskId.slice(0, 8)}…</Typography>
        <Chip
          size="small"
          label={data?.status || (isLoading ? 'loading' : 'unknown')}
          color={data?.status === 'completed' ? 'success' : data?.status === 'error' ? 'error' : 'default'}
        />
      </Box>
      <Typography variant="body2" sx={{ mb: 1 }}>
        Action: {data?.action || '—'} | Progress: {data?.progress || 0}/{data?.total || 0}
      </Typography>
      <LinearProgress variant="determinate" value={percent} />
      {data?.error_message && (
        <Alert severity="error" sx={{ mt: 1 }}>{data.error_message}</Alert>
      )}
    </Paper>
  );
}
