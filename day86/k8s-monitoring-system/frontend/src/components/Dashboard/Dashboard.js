import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
  Info
} from '@mui/icons-material';
import { healthApi, k8sApi, metricsApi } from '../../services/api';

function StatCard({ title, value, icon: Icon, color, subtitle }) {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
          <Box>
            <Typography color="text.secondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" sx={{ fontWeight: 600 }}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {subtitle}
              </Typography>
            )}
          </Box>
          <Icon sx={{ fontSize: 40, color }} />
        </Box>
      </CardContent>
    </Card>
  );
}

function HealthScoreCard({ score }) {
  const getColor = (score) => {
    if (score >= 80) return '#4caf50';
    if (score >= 60) return '#ff9800';
    return '#f44336';
  };

  const getStatus = (score) => {
    if (score >= 80) return 'Healthy';
    if (score >= 60) return 'Warning';
    return 'Critical';
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Cluster Health Score
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 3 }}>
          <Box sx={{ position: 'relative', display: 'inline-flex' }}>
            <CircularProgress
              variant="determinate"
              value={score || 0}
              size={120}
              thickness={5}
              sx={{ color: getColor(score || 0) }}
            />
            <Box
              sx={{
                top: 0,
                left: 0,
                bottom: 0,
                right: 0,
                position: 'absolute',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column'
              }}
            >
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
                {score ? Math.round(score) : 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {getStatus(score || 0)}
              </Typography>
            </Box>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

function Dashboard({ wsData }) {
  const [health, setHealth] = useState(null);
  const [pods, setPods] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [services, setServices] = useState([]);
  const [deployments, setDeployments] = useState([]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (wsData && wsData.type === 'health_update') {
      setHealth(wsData.data);
    }
  }, [wsData]);

  const fetchData = async () => {
    try {
      const [healthRes, podsRes, nodesRes, servicesRes, deploymentsRes] = await Promise.all([
        healthApi.getCurrent(),
        k8sApi.getPods(),
        k8sApi.getNodes(),
        k8sApi.getServices(),
        k8sApi.getDeployments()
      ]);

      setHealth(healthRes.data);
      setPods(podsRes.data);
      setNodes(nodesRes.data);
      setServices(servicesRes.data);
      setDeployments(deploymentsRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const runningPods = pods.filter(p => p.status === 'Running').length;
  const failedPods = pods.filter(p => p.status === 'Failed').length;
  const readyNodes = nodes.filter(n => n.status === 'Ready').length;

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <HealthScoreCard score={health?.overall_score} />
        </Grid>

        <Grid item xs={12} md={9}>
          <Grid container spacing={2}>
            <Grid item xs={6} md={3}>
              <StatCard
                title="Total Pods"
                value={pods.length}
                subtitle={`${runningPods} running`}
                icon={Info}
                color="#2196f3"
              />
            </Grid>
            <Grid item xs={6} md={3}>
              <StatCard
                title="Failed Pods"
                value={failedPods}
                subtitle={failedPods > 0 ? 'Attention needed' : 'All healthy'}
                icon={failedPods > 0 ? Error : CheckCircle}
                color={failedPods > 0 ? '#f44336' : '#4caf50'}
              />
            </Grid>
            <Grid item xs={6} md={3}>
              <StatCard
                title="Nodes"
                value={nodes.length}
                subtitle={`${readyNodes} ready`}
                icon={readyNodes === nodes.length ? CheckCircle : Warning}
                color={readyNodes === nodes.length ? '#4caf50' : '#ff9800'}
              />
            </Grid>
            <Grid item xs={6} md={3}>
              <StatCard
                title="Services"
                value={services.length}
                subtitle={`${deployments.length} deployments`}
                icon={Info}
                color="#9c27b0"
              />
            </Grid>
          </Grid>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Cluster Overview
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Node Health: {health?.node_health_score ? Math.round(health.node_health_score) : 0}%
                </Typography>
                <Box sx={{ width: '100%', bgcolor: 'grey.300', borderRadius: 1, height: 8, mt: 1 }}>
                  <Box
                    sx={{
                      width: `${health?.node_health_score || 0}%`,
                      bgcolor: health?.node_health_score >= 80 ? 'success.main' : 'warning.main',
                      height: 8,
                      borderRadius: 1
                    }}
                  />
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Pod Health: {health?.pod_health_score ? Math.round(health.pod_health_score) : 0}%
                </Typography>
                <Box sx={{ width: '100%', bgcolor: 'grey.300', borderRadius: 1, height: 8, mt: 1 }}>
                  <Box
                    sx={{
                      width: `${health?.pod_health_score || 0}%`,
                      bgcolor: health?.pod_health_score >= 80 ? 'success.main' : 'warning.main',
                      height: 8,
                      borderRadius: 1
                    }}
                  />
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
