import React from 'react'
import { 
  Box, 
  Typography, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Chip,
  CircularProgress 
} from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { dashboardAPI } from '../services/api'
import useFilterStore from '../store/filterStore'
import { format } from 'date-fns'

function DetailTable() {
  const { filters, timeRange } = useFilterStore()

  const { data, isLoading } = useQuery({
    queryKey: ['metrics', filters, timeRange],
    queryFn: () => dashboardAPI.getMetrics({
      start_time: timeRange.start.toISOString(),
      end_time: timeRange.end.toISOString(),
      ...filters
    }),
  })

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    )
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'success'
      case 'degraded': return 'warning'
      case 'critical': return 'error'
      default: return 'default'
    }
  }

  const recentMetrics = data?.metrics?.slice(-100) || []

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Recent Metrics ({recentMetrics.length} records)
      </Typography>
      
      <TableContainer sx={{ maxHeight: 400 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell>Timestamp</TableCell>
              <TableCell>Service</TableCell>
              <TableCell>Endpoint</TableCell>
              <TableCell>Region</TableCell>
              <TableCell>Metric</TableCell>
              <TableCell align="right">Value</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {recentMetrics.map((metric) => (
              <TableRow key={metric.id} hover>
                <TableCell>{format(new Date(metric.timestamp), 'yyyy-MM-dd HH:mm')}</TableCell>
                <TableCell>{metric.service}</TableCell>
                <TableCell>{metric.endpoint}</TableCell>
                <TableCell>{metric.region}</TableCell>
                <TableCell>{metric.metric_name}</TableCell>
                <TableCell align="right">{metric.value.toFixed(2)}</TableCell>
                <TableCell>
                  <Chip 
                    label={metric.status} 
                    size="small" 
                    color={getStatusColor(metric.status)}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}

export default DetailTable
