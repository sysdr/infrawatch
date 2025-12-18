import React from 'react'
import { Box, Typography, CircularProgress } from '@mui/material'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { useQuery } from '@tanstack/react-query'
import { dashboardAPI } from '../services/api'
import useFilterStore from '../store/filterStore'

function ServiceChart() {
  const { filters, timeRange, drillDown } = useFilterStore()

  const { data, isLoading } = useQuery({
    queryKey: ['aggregated', 'service', filters, timeRange],
    queryFn: () => dashboardAPI.getAggregated({
      start_time: timeRange.start.toISOString(),
      end_time: timeRange.end.toISOString(),
      group_by: 'service',
      metric_name: filters.metric_name || 'latency',
      ...filters
    }),
  })

  const handleBarClick = (data) => {
    if (data && data.dimension) {
      drillDown('service', data.dimension)
    }
  }

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    )
  }

  const chartData = data?.data || []

  if (chartData.length === 0) {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          Service Performance
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
          <Typography variant="body2" color="text.secondary">
            No data available for the selected time range and filters
          </Typography>
        </Box>
      </Box>
    )
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Service Performance
      </Typography>
      <Typography variant="caption" color="text.secondary" gutterBottom>
        Click bar to drill down
      </Typography>
      
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="dimension" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar 
            dataKey="value" 
            fill="#1976d2" 
            onClick={handleBarClick}
            cursor="pointer"
          />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  )
}

export default ServiceChart
