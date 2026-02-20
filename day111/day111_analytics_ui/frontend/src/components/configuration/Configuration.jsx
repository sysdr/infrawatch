import React, { useEffect, useState } from 'react';
import { Paper, Typography, Box, Grid, Switch, Slider, Chip, CircularProgress, Button } from '@mui/material';
import { Settings, CheckCircle, Error as ErrorIcon } from '@mui/icons-material';
import { configApi } from '../../api/client';
import useAnalyticsStore from '../../store/analyticsStore';

export default function Configuration() {
  const { config, setConfig } = useAnalyticsStore();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState('');

  useEffect(() => {
    configApi.getAll().then(r => { setConfig(r.data); setLoading(false); }).catch(() => setLoading(false));
  }, [setConfig]);

  const update = async (key, value) => {
    setSaving(key);
    try {
      await configApi.update(key, value);
      setConfig({ ...config, [key]: value });
    } finally { setSaving(''); }
  };

  if (loading) return <Box sx={{ display:'flex', justifyContent:'center', py:8 }}><CircularProgress sx={{ color:'#52b788' }}/></Box>;

  const thresholds = config.alert_thresholds || {};
  const prefs = config.ui_preferences || {};
  const dataSources = config.data_sources || [];

  return (
    <Box>
      <Typography variant="h5" sx={{ color: '#e8f5e9', fontWeight: 700, mb: 3 }}>Analytics Configuration</Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, background: '#1a2535', border: '1px solid #2a3f55', borderRadius: 2 }}>
            <Box sx={{ display:'flex', alignItems:'center', gap:1, mb:2 }}>
              <Settings sx={{ color:'#52b788' }}/>
              <Typography sx={{ color:'#e8f5e9', fontWeight:600 }}>Alert Thresholds</Typography>
            </Box>
            {Object.entries(thresholds).map(([key, val]) => (
              <Box key={key} sx={{ mb: 3 }}>
                <Box sx={{ display:'flex', justifyContent:'space-between', mb:1 }}>
                  <Typography sx={{ color:'#8899aa', fontSize:12 }}>{key.replace(/_/g,' ')}</Typography>
                  <Typography sx={{ color:'#52b788', fontSize:12, fontWeight:700 }}>{val}</Typography>
                </Box>
                <Slider value={val} min={0} max={key==='request_latency_ms' ? 1000 : 100} step={key==='request_latency_ms' ? 50 : 5}
                  onChange={(_, v) => update('alert_thresholds', {...thresholds, [key]: v})}
                  sx={{ color:'#52b788', '& .MuiSlider-thumb': { background:'#52b788' },
                        '& .MuiSlider-track': { background:'#40916c' } }}/>
                {saving === 'alert_thresholds' && <Typography sx={{ color:'#556677', fontSize:10 }}>Saving...</Typography>}
              </Box>
            ))}
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, background: '#1a2535', border: '1px solid #2a3f55', borderRadius: 2, mb: 2 }}>
            <Typography sx={{ color:'#e8f5e9', fontWeight:600, mb:2 }}>Data Sources</Typography>
            {dataSources.map((ds, i) => (
              <Box key={i} sx={{ display:'flex', alignItems:'center', justifyContent:'space-between', mb:1.5,
                                  p:1.5, background:'#0f1923', borderRadius:2, border:'1px solid #2a3f55' }}>
                <Box>
                  <Typography sx={{ color:'#e8f5e9', fontSize:13, fontWeight:600 }}>{ds.name}</Typography>
                  <Typography sx={{ color:'#556677', fontSize:11 }}>{ds.type}</Typography>
                </Box>
                {ds.status === 'healthy'
                  ? <Chip icon={<CheckCircle sx={{ fontSize:14 }}/>} label="Healthy" size="small"
                      sx={{ background:'#1b4332', color:'#52b788', fontSize:10 }}/>
                  : <Chip icon={<ErrorIcon sx={{ fontSize:14 }}/>} label="Degraded" size="small"
                      sx={{ background:'#7f1d1d', color:'#fca5a5', fontSize:10 }}/>}
              </Box>
            ))}
          </Paper>
          <Paper sx={{ p: 3, background: '#1a2535', border: '1px solid #2a3f55', borderRadius: 2 }}>
            <Typography sx={{ color:'#e8f5e9', fontWeight:600, mb:2 }}>UI Preferences</Typography>
            {Object.entries(prefs).map(([key, val]) => (
              <Box key={key} sx={{ display:'flex', alignItems:'center', justifyContent:'space-between', mb:1 }}>
                <Typography sx={{ color:'#8899aa', fontSize:12 }}>{key.replace(/_/g,' ')}</Typography>
                <Switch checked={Boolean(val)}
                  onChange={e => update('ui_preferences', {...prefs, [key]: e.target.checked})}
                  sx={{ '& .MuiSwitch-switchBase.Mui-checked': { color:'#52b788' },
                        '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': { background:'#40916c' } }}/>
              </Box>
            ))}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
