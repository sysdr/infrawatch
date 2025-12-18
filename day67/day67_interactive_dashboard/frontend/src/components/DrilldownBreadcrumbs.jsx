import React from 'react'
import { Box, Breadcrumbs, Link, Chip, Typography } from '@mui/material'
import HomeIcon from '@mui/icons-material/Home'
import NavigateNextIcon from '@mui/icons-material/NavigateNext'
import useFilterStore from '../store/filterStore'

function DrilldownBreadcrumbs() {
  const { drilldown, drillUp, resetDrilldown } = useFilterStore()

  if (drilldown.breadcrumbs.length === 0) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <HomeIcon sx={{ mr: 1 }} />
        <Typography variant="body2">All Services</Typography>
      </Box>
    )
  }

  return (
    <Breadcrumbs separator={<NavigateNextIcon fontSize="small" />}>
      <Link
        component="button"
        variant="body2"
        onClick={resetDrilldown}
        sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}
      >
        <HomeIcon sx={{ mr: 0.5 }} fontSize="inherit" />
        All
      </Link>
      
      {drilldown.breadcrumbs.map((crumb, index) => (
        <Link
          key={index}
          component="button"
          variant="body2"
          onClick={() => drillUp(index)}
          sx={{ cursor: 'pointer' }}
        >
          {crumb.dimension}: <strong>{crumb.value}</strong>
        </Link>
      ))}
    </Breadcrumbs>
  )
}

export default DrilldownBreadcrumbs
