import React, { useState } from 'react';
import { Grid, Paper, Typography, Box, Button, TextField, Chip, LinearProgress, Divider } from '@mui/material';
import { Psychology, Warning, CheckCircle } from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { mlApi } from '../../api/client';
import useAnalyticsStore from '../../store/analyticsStore';

const FEATURE_DEFAULTS = {
  cpu_utilization: 65, memory_usage: 72, request_latency_ms: 145,
  error_rate: 0.8, throughput_rps: 820, queue_depth: 18,
};

export default function MLInterface() {
  const { mlState, mlResult, setMlResult, setMlState } = useAnalyticsStore();
  const [features, setFeatures] = useState(FEATURE_DEFAULTS);

  const predict = async () => {
    setMlState('ML_REQUESTING');
    try {
      const r = await mlApi.predict({ features: Object.fromEntries(Object.entries(features).map(([k,v]) => [k, parseFloat(v)])) });
      setMlResult(r.data);
    } catch (_) { setMlState('IDLE'); }
  };

  const importanceData = mlResult
    ? Object.entries(mlResult.feature_importance)
        .map(([name, val]) => ({ name: name.replace(/_/g,'_').substring(0,12), full: name, val }))
        .sort((a,b) => b.val - a.val)
    : [];

  const isAnomaly = mlResult?.prediction === 'anomaly';

  return (
    <Box>
      <Typography variant="h5" sx={{ color: '#e8f5e9', fontWeight: 700, mb: 3, fontFamily: 'Inter' }}>
        ML Anomaly Predictor
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, background: '#1a2535', border: '1px solid #2a3f55', borderRadius: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Psychology sx={{ color: '#52b788' }} />
              <Typography sx={{ color: '#e8f5e9', fontWeight: 600 }}>Feature Input</Typography>
            </Box>
            <Grid container spacing={2}>
              {Object.entries(features).map(([key, val]) => (
                <Grid item xs={6} key={key}>
                  <TextField label={key.replace(/_/g,' ')} value={val} size="small" type="number"
                    onChange={e => setFeatures(f => ({...f, [key]: e.target.value}))}
                    InputLabelProps={{ style: { color: '#8899aa', fontSize: 11 } }}
                    InputProps={{ style: { color: '#e8f5e9', background: '#0f1923', borderRadius: 6, fontSize: 13 } }}
                    sx={{ '& .MuiOutlinedInput-notchedOutline': { borderColor: '#2a3f55' },
                          '& .MuiOutlinedInput-root:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#52b788' } }}
                    fullWidth variant="outlined"/>
                </Grid>
              ))}
            </Grid>
            <Button fullWidth variant="contained" onClick={predict} disabled={mlState === 'ML_REQUESTING'}
              sx={{ mt: 3, background: '#40916c', '&:hover': { background: '#52b788' },
                    color: 'white', fontWeight: 700, borderRadius: 2, py: 1.2 }}>
              {mlState === 'ML_REQUESTING' ? 'Predicting...' : 'Run Prediction'}
            </Button>
            {mlState === 'ML_REQUESTING' && <LinearProgress sx={{ mt: 1, borderRadius: 4, '& .MuiLinearProgress-bar': { background: '#52b788' } }}/>}
          </Paper>
        </Grid>

        <Grid item xs={12} md={7}>
          {mlResult && (
            <Paper sx={{ p: 3, background: '#1a2535', border: `1px solid ${isAnomaly ? '#d62828' : '#40916c'}`, borderRadius: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                {isAnomaly ? <Warning sx={{ color: '#d62828', fontSize: 32 }}/> : <CheckCircle sx={{ color: '#52b788', fontSize: 32 }}/>}
                <Box>
                  <Chip label={mlResult.prediction.toUpperCase()} size="small"
                        sx={{ background: isAnomaly ? '#7f1d1d' : '#1b4332', color: isAnomaly ? '#fca5a5' : '#52b788',
                              fontWeight: 700, letterSpacing: 1 }}/>
                  <Typography variant="caption" sx={{ color: '#8899aa', display: 'block', mt: 0.5 }}>
                    {(mlResult.probability * 100).toFixed(1)}% anomaly probability · confidence {(mlResult.confidence * 100).toFixed(1)}% · model v{mlResult.model_version}
                  </Typography>
                </Box>
              </Box>
              <Divider sx={{ borderColor: '#2a3f55', mb: 2 }}/>
              <Typography variant="caption" sx={{ color: '#8899aa', textTransform: 'uppercase', letterSpacing: 1 }}>
                Feature Importance
              </Typography>
              <Box sx={{ height: 220, mt: 1 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={importanceData} layout="vertical" margin={{ left: 80 }}>
                    <XAxis type="number" tick={{ fill: '#556677', fontSize: 10 }} />
                    <YAxis type="category" dataKey="name" tick={{ fill: '#8899aa', fontSize: 10 }} width={80}/>
                    <Tooltip contentStyle={{ background: '#1a2535', border: '1px solid #2a3f55', color: '#e8f5e9', fontSize: 11 }}
                             formatter={v => [v.toFixed(4), 'importance']}/>
                    <Bar dataKey="val" radius={[0,4,4,0]}>
                      {importanceData.map((e, i) => (
                        <Cell key={i} fill={i === 0 ? '#40916c' : i === 1 ? '#52b788' : '#74c69d'}/>
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </Paper>
          )}
          {!mlResult && (
            <Paper sx={{ p: 4, background: '#1a2535', border: '1px solid #2a3f55', borderRadius: 2,
                          display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: 200 }}>
              <Typography sx={{ color: '#556677' }}>Enter feature values and run prediction</Typography>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}
