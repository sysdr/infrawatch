import React, { useState } from 'react'
import { Box, Typography, CircularProgress, IconButton } from '@mui/material'
import ZoomOutMapIcon from '@mui/icons-material/ZoomOutMap'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  Brush
} from 'recharts'
import { useQuery } from '@tanstack/react-query'
import { dashboardAPI } from '../services/api'
import useFilterStore from '../store/filterStore'
import { format } from 'date-fns'

function TimeSeriesChart() {
  const { filters, timeRange, zoom, setZoom, clearZoom } = useFilterStore()
  const [brushDomain, setBrushDomain] = useState(null)

  const { data, isLoading } = useQuery({
    queryKey: ['timeseries', filters, timeRange, zoom],
    queryFn: () => dashboardAPI.getTimeSeries({
      start_time: timeRange.start.toISOString(),
      end_time: timeRange.end.toISOString(),
      metric_name: filters.metric_name || 'latency',
      interval: '5m',
      zoom_min: zoom.min,
      zoom_max: zoom.max,
      ...filters
    }),
  })

  const handleBrushChange = (domain) => {
    if (domain && domain.startIndex !== undefined && domain.endIndex !== undefined) {
      setBrushDomain(domain)
    }
  }

  const handleResetZoom = () => {
    clearZoom()
    setBrushDomain(null)
  }

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    )
  }

  const chartData = data?.data?.map(item => ({
    ...item,
    time: format(new Date(item.timestamp), 'HH:mm')
  })) || []

  if (chartData.length === 0) {
    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="h6">
            Time Series - {filters.metric_name || 'latency'}
          </Typography>
        </Box>
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="h6">
          Time Series - {filters.metric_name || 'latency'}
        </Typography>
        {brushDomain && (
          <IconButton size="small" onClick={handleResetZoom}>
            <ZoomOutMapIcon />
          </IconButton>
        )}
      </Box>
      
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="value" stroke="#1976d2" dot={false} />
          <Line type="monotone" dataKey="max" stroke="#dc004e" dot={false} strokeDasharray="3 3" />
          <Brush 
            dataKey="time" 
            height={30} 
            stroke="#1976d2"
            onChange={handleBrushChange}
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  )
}

export default TimeSeriesChart
