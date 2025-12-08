import React, { useState, useEffect } from 'react';
import { Paper, Typography, Box, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, ComposedChart } from 'recharts';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

function PredictionsChart({ metrics, selectedMetric, onMetricChange }) {
  const [predictions, setPredictions] = useState([]);

  useEffect(() => {
    fetchPredictions();
    const interval = setInterval(fetchPredictions, 60000);
    return () => clearInterval(interval);
  }, [selectedMetric]);

  const fetchPredictions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/predictions/${selectedMetric}?hours_ahead=24`);
      setPredictions(response.data.predictions);
    } catch (error) {
      console.error('Error fetching predictions:', error);
    }
  };

  const chartData = predictions.map(p => ({
    hour: p.hours_ahead,
    predicted: p.prediction,
    lower: p.confidence_lower,
    upper: p.confidence_upper
  }));

  return (
    <Paper sx={{ p: 3, borderRadius: 2, border: '1px solid #e5e7eb' }}>
      <Box sx={{ mb: 3 }}>
        <FormControl fullWidth>
          <InputLabel sx={{ color: '#6b7280' }}>Metric</InputLabel>
          <Select 
            value={selectedMetric} 
            onChange={(e) => onMetricChange(e.target.value)} 
            label="Metric"
            sx={{
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#e5e7eb'
              }
            }}
          >
            {metrics.map(m => <MenuItem key={m} value={m}>{m}</MenuItem>)}
          </Select>
        </FormControl>
      </Box>

      <Typography variant="h6" gutterBottom sx={{ color: '#1f2937', fontWeight: 600 }}>24-Hour Forecast</Typography>
      
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="hour" stroke="#6b7280" label={{ value: 'Hours Ahead', position: 'insideBottom', offset: -5, fill: '#6b7280' }} />
          <YAxis stroke="#6b7280" />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1f2937', 
              border: '1px solid #374151',
              borderRadius: 8
            }} 
          />
          <Legend />
          <Area type="monotone" dataKey="upper" fill="#10b981" fillOpacity={0.15} stroke="none" />
          <Area type="monotone" dataKey="lower" fill="#10b981" fillOpacity={0.15} stroke="none" />
          <Line type="monotone" dataKey="predicted" stroke="#059669" strokeWidth={3} name="Predicted Value" dot={{ fill: '#10b981', r: 4 }} />
        </ComposedChart>
      </ResponsiveContainer>
    </Paper>
  );
}

export default PredictionsChart;
