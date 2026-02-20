import React, { useState } from 'react';
import { Paper, Typography, Box, Button, Checkbox, FormControlLabel, Grid, CircularProgress, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import { analyticsApi } from '../../api/client';
import useAnalyticsStore from '../../store/analyticsStore';

const METRICS = ['cpu_utilization','memory_usage','request_latency_ms','error_rate','throughput_rps','queue_depth','disk_io_mbps','network_out_mbps'];

function getColor(v) {
  if (v >= 0.7) return '#1b4332';
  if (v >= 0.4) return '#40916c';
  if (v >= 0.1) return '#74c69d';
  if (v >= -0.1) return '#e8f5e9';
  if (v >= -0.4) return '#fecdd3';
  if (v >= -0.7) return '#fca5a5';
  return '#b91c1c';
}

function getTextColor(v) { return Math.abs(v) > 0.4 ? '#ffffff' : '#2d3748'; }

export default function CorrelationViewer() {
  const [selected, setSelected] = useState(['cpu_utilization','memory_usage','request_latency_ms','error_rate']);
  const [method, setMethod] = useState('pearson');
  const [hours, setHours] = useState(6);
  const { corrState, corrMatrix, corrLabels, setCorrResult, setCorrState } = useAnalyticsStore();

  const toggle = (m) => setSelected(s => s.includes(m) ? s.filter(x=>x!==m) : [...s, m].slice(0,8));
  const compute = async () => {
    if (selected.length < 2) return;
    setCorrState('CORRELATING');
    try {
      const r = await analyticsApi.computeCorrelation({ metrics: selected, time_window_hours: hours, method });
      setCorrResult(r.data.matrix, r.data.labels);
    } catch (_) { setCorrState('IDLE'); }
  };

  return (
    <Box>
      <Typography variant="h5" sx={{ color: '#e8f5e9', fontWeight: 700, mb: 3 }}>Correlation Viewer</Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, background: '#1a2535', border: '1px solid #2a3f55', borderRadius: 2 }}>
            <Typography sx={{ color: '#e8f5e9', fontWeight: 600, mb: 2 }}>Select Metrics (2-8)</Typography>
            {METRICS.map(m => (
              <FormControlLabel key={m} control={
                <Checkbox checked={selected.includes(m)} onChange={() => toggle(m)} size="small"
                  sx={{ color: '#40916c', '&.Mui-checked': { color: '#52b788' } }}/>
              } label={<Typography sx={{ color: '#8899aa', fontSize: 12 }}>{m.replace(/_/g,' ')}</Typography>}
              sx={{ display: 'block', mb: 0.5 }}/>
            ))}
            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              <FormControl size="small" sx={{ flex: 1 }}>
                <InputLabel sx={{ color: '#8899aa' }}>Method</InputLabel>
                <Select value={method} onChange={e => setMethod(e.target.value)} label="Method"
                  sx={{ color: '#e8f5e9', background: '#0f1923', '& .MuiOutlinedInput-notchedOutline': { borderColor: '#2a3f55' } }}>
                  <MenuItem value="pearson">Pearson</MenuItem>
                  <MenuItem value="spearman">Spearman</MenuItem>
                </Select>
              </FormControl>
              <FormControl size="small" sx={{ flex: 1 }}>
                <InputLabel sx={{ color: '#8899aa' }}>Window</InputLabel>
                <Select value={hours} onChange={e => setHours(e.target.value)} label="Window"
                  sx={{ color: '#e8f5e9', background: '#0f1923', '& .MuiOutlinedInput-notchedOutline': { borderColor: '#2a3f55' } }}>
                  {[1,2,6,12,24].map(h => <MenuItem key={h} value={h}>{h}h</MenuItem>)}
                </Select>
              </FormControl>
            </Box>
            <Button fullWidth variant="contained" onClick={compute} disabled={selected.length < 2 || corrState === 'CORRELATING'}
              sx={{ mt: 2, background: '#40916c', '&:hover': { background: '#52b788' }, color: 'white', fontWeight: 700, borderRadius: 2 }}>
              {corrState === 'CORRELATING' ? 'Computing...' : 'Compute Matrix'}
            </Button>
          </Paper>
        </Grid>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, background: '#1a2535', border: '1px solid #2a3f55', borderRadius: 2, minHeight: 300 }}>
            {corrState === 'CORRELATING' && (
              <Box sx={{ display:'flex', justifyContent:'center', alignItems:'center', height: 250 }}>
                <CircularProgress sx={{ color: '#52b788' }}/>
              </Box>
            )}
            {corrMatrix && corrState === 'CORR_DONE' && (
              <Box>
                <Typography sx={{ color: '#8899aa', mb: 2, fontSize: 12, textTransform: 'uppercase', letterSpacing: 1 }}>
                  {method.charAt(0).toUpperCase()+method.slice(1)} Correlation Matrix · {hours}h window
                </Typography>
                <Box sx={{ overflowX: 'auto' }}>
                  <table style={{ borderCollapse: 'collapse', width: '100%' }}>
                    <thead>
                      <tr>
                        <th style={{ width: 100 }}></th>
                        {corrLabels.map(l => (
                          <th key={l} style={{ color: '#8899aa', fontSize: 9, fontWeight: 600,
                                               padding: '4px 2px', textTransform: 'uppercase', maxWidth: 70,
                                               overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {l.replace(/_/g,' ').substring(0,10)}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {corrMatrix.map((row, i) => (
                        <tr key={i}>
                          <td style={{ color: '#8899aa', fontSize: 9, paddingRight: 8, textAlign: 'right',
                                        whiteSpace: 'nowrap', maxWidth: 100, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {corrLabels[i]?.replace(/_/g,' ').substring(0,10)}
                          </td>
                          {row.map((val, j) => (
                            <td key={j} style={{ background: getColor(val), color: getTextColor(val),
                                                  width: 56, height: 44, textAlign: 'center', fontSize: 11,
                                                  fontWeight: 600, borderRadius: 4, padding: 2 }}>
                              {val.toFixed(2)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </Box>
                <Box sx={{ display: 'flex', gap: 2, mt: 2, alignItems: 'center' }}>
                  {[['#b91c1c','Strong -'],['#fca5a5','Weak -'],['#e8f5e9','None'],['#74c69d','Weak +'],['#1b4332','Strong +']].map(([c,l]) => (
                    <Box key={l} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Box sx={{ width: 14, height: 14, background: c, borderRadius: 2 }}/>
                      <Typography sx={{ color: '#556677', fontSize: 10 }}>{l}</Typography>
                    </Box>
                  ))}
                </Box>
              </Box>
            )}
            {!corrMatrix && corrState !== 'CORRELATING' && (
              <Box sx={{ display:'flex', justifyContent:'center', alignItems:'center', height: 250 }}>
                <Typography sx={{ color: '#556677' }}>Select metrics and compute to view the heat map</Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
