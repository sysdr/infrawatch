import React, { useEffect } from 'react'
import { 
  Box, 
  Grid, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem,
  Chip,
  Button 
} from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { filtersAPI } from '../services/api'
import useFilterStore from '../store/filterStore'

function FilterPanel() {
  const { filters, setFilter, clearFilter, clearAllFilters } = useFilterStore()

  // Fetch available filters without the current dimension's filter
  // This ensures each select always shows all available options
  const { data: availableFilters } = useQuery({
    queryKey: ['filters', 'available', filters],
    queryFn: () => filtersAPI.getAvailable(filters),
  })

  // Auto-select first metric when metrics are loaded and no metric is selected
  useEffect(() => {
    if (availableFilters?.metrics?.length > 0 && !filters.metric_name) {
      setFilter('metric_name', availableFilters.metrics[0])
    }
  }, [availableFilters?.metrics, filters.metric_name, setFilter])

  // Clear invalid filter values that aren't in available options
  useEffect(() => {
    if (!availableFilters) return
    
    const dimensions = [
      { key: 'service', options: availableFilters.services },
      { key: 'endpoint', options: availableFilters.endpoints },
      { key: 'region', options: availableFilters.regions },
      { key: 'environment', options: availableFilters.environments },
      { key: 'metric_name', options: availableFilters.metrics },
      { key: 'status', options: availableFilters.statuses }
    ]
    
    dimensions.forEach(({ key, options }) => {
      const currentValue = filters[key]
      if (currentValue && options && options.length > 0 && !options.includes(currentValue)) {
        clearFilter(key)
      }
    })
  }, [availableFilters, filters, clearFilter])

  const handleFilterChange = (dimension, value) => {
    if (value === '') {
      clearFilter(dimension)
    } else {
      setFilter(dimension, value)
    }
  }

  // Helper to get safe value for Select - only use if it's in available options
  const getSafeValue = (dimension, availableOptions) => {
    const currentValue = filters[dimension]
    if (!currentValue) return ''
    // If current value is in available options, use it
    if (availableOptions && availableOptions.length > 0 && availableOptions.includes(currentValue)) {
      return currentValue
    }
    // If value is set but not in options (or options are empty), return empty
    // The useEffect will clear invalid filters
    return ''
  }

  const activeFilterCount = Object.values(filters).filter(v => v !== null).length

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box>
          {activeFilterCount > 0 && (
            <Chip 
              label={`${activeFilterCount} filters active`} 
              size="small" 
              color="primary" 
              sx={{ mr: 1 }}
            />
          )}
        </Box>
        <Button size="small" onClick={clearAllFilters}>
          Clear All
        </Button>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel>Service</InputLabel>
            <Select
              value={getSafeValue('service', availableFilters?.services)}
              onChange={(e) => handleFilterChange('service', e.target.value)}
              label="Service"
            >
              <MenuItem value="">All</MenuItem>
              {availableFilters?.services?.map((service) => (
                <MenuItem key={service} value={service}>{service}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel>Endpoint</InputLabel>
            <Select
              value={getSafeValue('endpoint', availableFilters?.endpoints)}
              onChange={(e) => handleFilterChange('endpoint', e.target.value)}
              label="Endpoint"
            >
              <MenuItem value="">All</MenuItem>
              {availableFilters?.endpoints?.map((endpoint) => (
                <MenuItem key={endpoint} value={endpoint}>{endpoint}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel>Region</InputLabel>
            <Select
              value={getSafeValue('region', availableFilters?.regions)}
              onChange={(e) => handleFilterChange('region', e.target.value)}
              label="Region"
            >
              <MenuItem value="">All</MenuItem>
              {availableFilters?.regions?.map((region) => (
                <MenuItem key={region} value={region}>{region}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel>Environment</InputLabel>
            <Select
              value={getSafeValue('environment', availableFilters?.environments)}
              onChange={(e) => handleFilterChange('environment', e.target.value)}
              label="Environment"
            >
              <MenuItem value="">All</MenuItem>
              {availableFilters?.environments?.map((env) => (
                <MenuItem key={env} value={env}>{env}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel>Metric</InputLabel>
            <Select
              value={getSafeValue('metric_name', availableFilters?.metrics)}
              onChange={(e) => handleFilterChange('metric_name', e.target.value)}
              label="Metric"
            >
              {availableFilters?.metrics?.map((metric) => (
                <MenuItem key={metric} value={metric}>{metric}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel>Status</InputLabel>
            <Select
              value={getSafeValue('status', availableFilters?.statuses)}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              label="Status"
            >
              <MenuItem value="">All</MenuItem>
              {availableFilters?.statuses?.map((status) => (
                <MenuItem key={status} value={status}>{status}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>
    </Box>
  )
}

export default FilterPanel
