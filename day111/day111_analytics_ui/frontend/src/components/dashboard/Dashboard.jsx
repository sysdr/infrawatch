import React, { useEffect } from 'react';
import { Grid, Paper, Typography, Box, Chip, CircularProgress } from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';
import { ResponsiveContainer, AreaChart, Area, Tooltip } from 'recharts';
import useAnalyticsStore from '../../store/analyticsStore';
import { analyticsApi } from '../../api/client';
import { useWebSocket } from '../../hooks/useWebSocket';

const METRIC_COLORS = {
  cpu_utilization: '#52b788', memory_usage: '#40916c',
  request_latency_ms: '#74c69d', error_rate: '#d62828',
  throughput_rps: '#95d5b2', queue_depth: '#b7e4c7',
  disk_io_mbps: '#52b788', network_out_mbps: '#40916c',
};

function KPICard({ kpi }) {
  const color = METRIC_COLORS[kpi.name] || '#52b788';
  const sparkData = (kpi.sparkline || []).map((v, i) => ({ i, v }));
  return (
    <Paper sx={{ p: 2, background: '#1a2535', border: '1px solid #2a3f55', borderRadius: 2,
                 boxShadow: '0 4px 20px rgba(0,0,0,0.3)', '&:hover': { border: '1px solid #52b788' }, transition: 'all 0.2s' }}>
      <Typography variant="caption" sx={{ color: '#8899aa', textTransform: 'uppercase', letterSpacing: 1, fontSize: 10 }}>
        {kpi.name.replace(/_/g, ' ')}
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1, mt: 0.5 }}>
        <Typography variant="h4" sx={{ color: '#e8f5e9', fontWeight: 700, fontFamily: 'Inter' }}>
          {kpi.value.toFixed(1)}
        </Typography>
        <Typography variant="caption" sx={{ color: '#8899aa' }}>{kpi.unit}</Typography>
      </Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
        {kpi.trend_direction === 'up'
          ? <TrendingUp sx={{ fontSize: 16, color: kpi.name === 'error_rate' ? '#d62828' : '#52b788' }} />
          : <TrendingDown sx={{ fontSize: 16, color: '#52b788' }} />}
        <Typography variant="caption" sx={{ color: kpi.trend_direction === 'up' && kpi.name !== 'error_rate' ? '#52b788' : '#8899aa' }}>
          {kpi.trend > 0 ? '+' : ''}{kpi.trend.toFixed(1)}%
        </Typography>
      </Box>
      <Box sx={{ height: 50, mt: 1 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={sparkData}>
            <defs>
              <linearGradient id={`grad-${kpi.name}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.4}/>
                <stop offset="95%" stopColor={color} stopOpacity={0}/>
              </linearGradient>
            </defs>
            <Area type="monotone" dataKey="v" stroke={color} strokeWidth={1.5}
                  fill={`url(#grad-${kpi.name})`} dot={false} isAnimationActive={false}/>
            <Tooltip contentStyle={{ background: '#1a2535', border: '1px solid #2a3f55', borderRadius: 6,
                                      color: '#e8f5e9', fontSize: 11 }} formatter={(v) => [v.toFixed(2), kpi.unit]}/>
          </AreaChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
}

export default function Dashboard() {
  const { kpis, dashboardState, lastUpdated } = useAnalyticsStore();
  useWebSocket();

  useEffect(() => {
    analyticsApi.getDashboard().then(r => {
      useAnalyticsStore.getState().setKpis(r.data.kpis, r.data.updated_at);
    }).catch(() => useAnalyticsStore.getState().setDashboardState('ERROR'));
  }, []);

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h5" sx={{ color: '#e8f5e9', fontWeight: 700, fontFamily: 'Inter' }}>
          Infrastructure Dashboard
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {dashboardState === 'REFRESHING' && <CircularProgress size={14} sx={{ color: '#52b788' }} />}
          <Chip label={dashboardState} size="small"
                sx={{ background: dashboardState === 'READY' ? '#1b4332' : '#2a3f55',
                      color: '#52b788', border: '1px solid #40916c', fontSize: 10 }}/>
          {lastUpdated && (
            <Typography variant="caption" sx={{ color: '#556677' }}>
              {new Date(lastUpdated).toLocaleTimeString()}
            </Typography>
          )}
        </Box>
      </Box>

      {kpis.length === 0 && dashboardState === 'LOADING' ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress sx={{ color: '#52b788' }} />
        </Box>
      ) : (
        <Grid container spacing={2}>
          {kpis.map(kpi => (
            <Grid item xs={12} sm={6} md={3} key={kpi.name}>
              <KPICard kpi={kpi} />
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
