import React from 'react'
import { Grid, Paper, Typography, Box } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { dashboardAPI } from '../services/api'
import useFilterStore from '../store/filterStore'

function MetricCards() {
  const { filters, timeRange } = useFilterStore()

  const metrics = ['latency', 'error_rate', 'request_count']

  return (
    <Grid container spacing={2}>
      {metrics.map(metric => (
        <Grid item xs={12} sm={4} key={metric}>
          <MetricCard metric={metric} filters={filters} timeRange={timeRange} />
        </Grid>
      ))}
    </Grid>
  )
}

function MetricCard({ metric, filters, timeRange }) {
  const { data } = useQuery({
    queryKey: ['aggregated', 'overall', metric, filters, timeRange],
    queryFn: () => dashboardAPI.getAggregated({
      start_time: timeRange.start.toISOString(),
      end_time: timeRange.end.toISOString(),
      group_by: 'service',
      metric_name: metric,
      aggregation: 'avg',
      ...filters
    }),
  })

  const avgValue = data?.data?.reduce((sum, item) => sum + item.value, 0) / (data?.data?.length || 1) || 0

  return (
    <Paper sx={{ p: 2, textAlign: 'center' }}>
      <Typography variant="h4" color="primary">
        {avgValue.toFixed(2)}
      </Typography>
      <Typography variant="subtitle2" color="text.secondary">
        {metric.replace('_', ' ').toUpperCase()}
      </Typography>
    </Paper>
  )
}

export default MetricCards
