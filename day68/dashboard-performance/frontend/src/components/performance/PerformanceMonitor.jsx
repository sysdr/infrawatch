import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Box, LinearProgress } from '@mui/material';

function PerformanceMonitor() {
  const [metrics, setMetrics] = useState({
    fps: 60,
    memory: 0,
    renderTime: 0
  });

  useEffect(() => {
    let frameCount = 0;
    let lastTime = performance.now();
    
    const measureFPS = () => {
      frameCount++;
      const currentTime = performance.now();
      
      if (currentTime >= lastTime + 1000) {
        setMetrics(prev => ({
          ...prev,
          fps: frameCount,
          memory: performance.memory ? Math.round(performance.memory.usedJSHeapSize / 1048576) : 0
        }));
        
        frameCount = 0;
        lastTime = currentTime;
      }
      
      requestAnimationFrame(measureFPS);
    };
    
    measureFPS();
  }, []);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Performance Metrics</Typography>
        
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="body2">FPS</Typography>
            <Typography variant="body2" fontWeight="bold">{metrics.fps}</Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={(metrics.fps / 60) * 100} 
            color={metrics.fps >= 55 ? 'success' : 'warning'}
          />
        </Box>
        
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="body2">Memory</Typography>
            <Typography variant="body2" fontWeight="bold">{metrics.memory} MB</Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={Math.min((metrics.memory / 100) * 100, 100)} 
          />
        </Box>
      </CardContent>
    </Card>
  );
}

export default PerformanceMonitor;
