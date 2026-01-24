import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Box, Paper, Typography, CircularProgress, Grid, Card, CardContent } from '@mui/material';
import { fetchTopology, updateMetric } from '../store/resourceSlice';
import websocketService from '../services/websocket';

function TopologyView() {
  const dispatch = useDispatch();
  const { topology, loading } = useSelector(state => state.resources);
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    dispatch(fetchTopology());
    
    // Subscribe to WebSocket updates
    websocketService.subscribe('metric_update', (data) => {
      dispatch(updateMetric(data));
    });
  }, [dispatch]);

  const getHealthColor = (health) => {
    const colors = {
      green: '#4caf50',
      yellow: '#ff9800',
      red: '#f44336',
      gray: '#9e9e9e'
    };
    return colors[health] || colors.gray;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12} md={9}>
          <Paper elevation={3} sx={{ p: 3, minHeight: 600 }}>
            <Typography variant="h5" gutterBottom>
              Infrastructure Topology
            </Typography>
            
            <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Typography variant="body2" sx={{ px: 2, py: 0.5, bgcolor: '#e8f5e9', borderRadius: 1 }}>
                Healthy: {topology.stats?.healthy || 0}
              </Typography>
              <Typography variant="body2" sx={{ px: 2, py: 0.5, bgcolor: '#fff3e0', borderRadius: 1 }}>
                Warning: {topology.stats?.warning || 0}
              </Typography>
              <Typography variant="body2" sx={{ px: 2, py: 0.5, bgcolor: '#ffebee', borderRadius: 1 }}>
                Critical: {topology.stats?.critical || 0}
              </Typography>
            </Box>

            <Box sx={{ mt: 3, position: 'relative', height: 500, border: '1px solid #e0e0e0', borderRadius: 1 }}>
              <svg width="100%" height="100%">
                {/* Draw edges */}
                {topology.edges?.map((edge, idx) => {
                  const source = topology.nodes.find(n => n.id === edge.source);
                  const target = topology.nodes.find(n => n.id === edge.target);
                  if (!source || !target || !source.position || !target.position) return null;
                  
                  return (
                    <line
                      key={idx}
                      x1={source.position[0]}
                      y1={source.position[1]}
                      x2={target.position[0]}
                      y2={target.position[1]}
                      stroke="#bdbdbd"
                      strokeWidth="2"
                    />
                  );
                })}
                
                {/* Draw nodes */}
                {topology.nodes?.map((node) => {
                  if (!node.position) return null;
                  const [x, y] = node.position;
                  return (
                    <g key={node.id} onClick={() => setSelectedNode(node)}>
                      <circle
                        cx={x}
                        cy={y}
                        r="20"
                        fill={getHealthColor(node.health)}
                        stroke="#fff"
                        strokeWidth="2"
                        style={{ cursor: 'pointer' }}
                      />
                      <text
                        x={x}
                        y={y + 35}
                        textAnchor="middle"
                        fontSize="10"
                        fill="#424242"
                      >
                        {node.name.length > 12 ? node.name.substring(0, 12) + '...' : node.name}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={3}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              {selectedNode ? 'Resource Details' : 'Select a Resource'}
            </Typography>
            {selectedNode && (
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Name: {selectedNode.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Type: {selectedNode.type}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Provider: {selectedNode.provider}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Region: {selectedNode.region}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Status: {selectedNode.status}
                </Typography>
                <Typography variant="body2" sx={{ mt: 2, fontWeight: 'bold' }}>
                  Tags:
                </Typography>
                {Object.entries(selectedNode.tags || {}).map(([key, value]) => (
                  <Typography key={key} variant="body2" color="text.secondary">
                    {key}: {value}
                  </Typography>
                ))}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default TopologyView;
