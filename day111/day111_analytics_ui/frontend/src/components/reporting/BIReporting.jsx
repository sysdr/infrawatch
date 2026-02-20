import React, { useState, useEffect } from 'react';
import { Paper, Typography, Box, Button, TextField, Select, MenuItem, FormControl, InputLabel, Grid, Chip, Table, TableHead, TableBody, TableRow, TableCell } from '@mui/material';
import { Assessment, Download, Add } from '@mui/icons-material';
import { reportsApi } from '../../api/client';
import useAnalyticsStore from '../../store/analyticsStore';

const METRICS = ['cpu_utilization','memory_usage','request_latency_ms','error_rate','throughput_rps','queue_depth'];

export default function BIReporting() {
  const { reports, setReports } = useAnalyticsStore();
  const [name, setName] = useState('');
  const [format, setFormat] = useState('csv');
  const [selectedMetrics, setSelectedMetrics] = useState(['cpu_utilization','memory_usage']);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    reportsApi.list().then(r => setReports(r.data)).catch(() => {});
  }, [setReports]);

  const create = async () => {
    if (!name.trim()) return;
    setCreating(true);
    try {
      await reportsApi.create({ name, config: { metrics: selectedMetrics }, output_format: format });
      const r = await reportsApi.list();
      setReports(r.data);
      setName('');
    } finally { setCreating(false); }
  };

  const download = (id, fmt) => window.open(fmt === 'csv' ? reportsApi.exportCsv(id) : reportsApi.exportPdf(id), '_blank');

  const toggleMetric = (m) => setSelectedMetrics(s => s.includes(m) ? s.filter(x=>x!==m) : [...s, m]);

  const inputSx = { color: '#e8f5e9', background: '#0f1923', '& .MuiOutlinedInput-notchedOutline': { borderColor: '#2a3f55' },
                     '& .MuiOutlinedInput-root:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#52b788' } };

  return (
    <Box>
      <Typography variant="h5" sx={{ color: '#e8f5e9', fontWeight: 700, mb: 3 }}>BI Reporting</Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, background: '#1a2535', border: '1px solid #2a3f55', borderRadius: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Add sx={{ color: '#52b788' }} /><Typography sx={{ color: '#e8f5e9', fontWeight: 600 }}>Create Report</Typography>
            </Box>
            <TextField fullWidth label="Report Name" value={name} onChange={e => setName(e.target.value)}
              size="small" variant="outlined" sx={{ mb: 2 }}
              InputLabelProps={{ style: { color: '#8899aa' } }} InputProps={{ style: inputSx }}/>
            <FormControl fullWidth size="small" sx={{ mb: 2 }}>
              <InputLabel sx={{ color: '#8899aa' }}>Output Format</InputLabel>
              <Select value={format} onChange={e => setFormat(e.target.value)} label="Output Format" sx={inputSx}>
                <MenuItem value="csv">CSV</MenuItem>
                <MenuItem value="pdf">PDF</MenuItem>
              </Select>
            </FormControl>
            <Typography sx={{ color: '#8899aa', fontSize: 11, mb: 1, textTransform: 'uppercase', letterSpacing: 1 }}>Metrics</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.8, mb: 2 }}>
              {METRICS.map(m => (
                <Chip key={m} label={m.replace(/_/g,' ')} size="small" clickable
                  onClick={() => toggleMetric(m)}
                  sx={{ background: selectedMetrics.includes(m) ? '#1b4332' : '#0f1923',
                        color: selectedMetrics.includes(m) ? '#52b788' : '#556677',
                        border: selectedMetrics.includes(m) ? '1px solid #40916c' : '1px solid #2a3f55',
                        fontSize: 10 }}/>
              ))}
            </Box>
            <Button fullWidth variant="contained" onClick={create} disabled={creating || !name.trim()}
              sx={{ background: '#40916c', '&:hover': { background: '#52b788' }, color: 'white', fontWeight: 700, borderRadius: 2 }}>
              {creating ? 'Creating...' : 'Create Report'}
            </Button>
          </Paper>
        </Grid>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3, background: '#1a2535', border: '1px solid #2a3f55', borderRadius: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Assessment sx={{ color: '#52b788' }} /><Typography sx={{ color: '#e8f5e9', fontWeight: 600 }}>Reports</Typography>
            </Box>
            {reports.length === 0 ? (
              <Typography sx={{ color: '#556677', textAlign: 'center', py: 4 }}>No reports yet. Create one to get started.</Typography>
            ) : (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    {['Name','Format','Created','Export'].map(h => (
                      <TableCell key={h} sx={{ color: '#8899aa', borderColor: '#2a3f55', fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.5 }}>{h}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {reports.map(r => (
                    <TableRow key={r.id} sx={{ '&:hover': { background: '#0f1923' } }}>
                      <TableCell sx={{ color: '#e8f5e9', borderColor: '#2a3f55', fontSize: 12 }}>{r.name}</TableCell>
                      <TableCell sx={{ borderColor: '#2a3f55' }}>
                        <Chip label={r.output_format.toUpperCase()} size="small"
                          sx={{ background: '#1b4332', color: '#52b788', fontSize: 9 }}/>
                      </TableCell>
                      <TableCell sx={{ color: '#8899aa', borderColor: '#2a3f55', fontSize: 11 }}>
                        {new Date(r.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell sx={{ borderColor: '#2a3f55' }}>
                        <Button size="small" startIcon={<Download sx={{ fontSize: 14 }}/>}
                          onClick={() => download(r.id, r.output_format)}
                          sx={{ color: '#52b788', fontSize: 11, textTransform: 'none', minWidth: 0,
                                '&:hover': { background: '#1b4332' } }}>
                          Export
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
