import React, { useState } from 'react'
import { Box, Grid, Paper } from '@mui/material'
import TimeRangeSelector from './TimeRangeSelector'
import FilterPanel from './FilterPanel'
import DrilldownBreadcrumbs from './DrilldownBreadcrumbs'
import ServiceChart from './ServiceChart'
import TimeSeriesChart from './TimeSeriesChart'
import MetricCards from './MetricCards'
import DetailTable from './DetailTable'

function InteractiveDashboard() {
  return (
    <Box>
      {/* Top Controls */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TimeRangeSelector />
          </Grid>
          <Grid item xs={12} md={6}>
            <DrilldownBreadcrumbs />
          </Grid>
        </Grid>
      </Paper>

      {/* Filter Panel */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <FilterPanel />
      </Paper>

      {/* Metric Cards */}
      <Box sx={{ mb: 3 }}>
        <MetricCards />
      </Box>

      {/* Charts Grid */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <ServiceChart />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <TimeSeriesChart />
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <DetailTable />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default InteractiveDashboard
