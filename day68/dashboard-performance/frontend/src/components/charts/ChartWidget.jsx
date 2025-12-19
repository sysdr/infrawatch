import React, { useState, useEffect, useRef, memo } from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { dashboardAPI } from '../../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const ChartWidget = memo(({ widget, realtimeUpdate }) => {
  const [chartData, setChartData] = useState(null);
  const [renderTime, setRenderTime] = useState(0);
  const mountTimeRef = useRef(Date.now());

  useEffect(() => {
    loadChartData();
  }, [widget.id]);

  useEffect(() => {
    if (realtimeUpdate && chartData) {
      // Update chart with new real-time data
      updateChartWithRealtime(realtimeUpdate);
    }
  }, [realtimeUpdate]);

  const loadChartData = async () => {
    const startTime = performance.now();
    
    try {
      const data = await dashboardAPI.getWidgetData(widget.id);
      
      if (data.type === 'line') {
        setChartData({
          labels: data.data.map(d => new Date(d.timestamp).toLocaleTimeString()),
          datasets: [{
            label: widget.title,
            data: data.data.map(d => d.value),
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            tension: 0.4,
          }]
        });
      }
      
      const endTime = performance.now();
      setRenderTime(Math.round(endTime - startTime));
    } catch (error) {
      console.error('Error loading chart data:', error);
    }
  };

  const updateChartWithRealtime = (update) => {
    setChartData(prev => {
      if (!prev) return prev;
      
      const newData = [...prev.datasets[0].data];
      newData.shift();
      newData.push(update.value);
      
      return {
        ...prev,
        datasets: [{
          ...prev.datasets[0],
          data: newData
        }]
      };
    });
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 0  // Disable animation for performance
    },
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100
      }
    }
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1, pb: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="subtitle1" component="div">
            {widget.title}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {renderTime}ms
          </Typography>
        </Box>
        
        <Box sx={{ height: 250 }}>
          {chartData ? (
            <Line data={chartData} options={options} />
          ) : (
            <Typography variant="body2" color="text.secondary">Loading...</Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  );
});

export default ChartWidget;
