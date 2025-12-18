import React from 'react'
import { Box, Button, ButtonGroup, Typography } from '@mui/material'
import { subHours, subDays } from 'date-fns'
import useFilterStore from '../store/filterStore'

const PRESETS = [
  { label: 'Last 15m', value: 'last_15m', hours: 0.25 },
  { label: 'Last 1h', value: 'last_1h', hours: 1 },
  { label: 'Last 6h', value: 'last_6h', hours: 6 },
  { label: 'Last 24h', value: 'last_24h', hours: 24 },
  { label: 'Last 7d', value: 'last_7d', days: 7 },
]

function TimeRangeSelector() {
  const { timeRange, setTimeRange } = useFilterStore()

  const handlePresetClick = (preset) => {
    const end = new Date()
    const start = preset.days 
      ? subDays(end, preset.days)
      : subHours(end, preset.hours)
    
    setTimeRange({
      start,
      end,
      preset: preset.value
    })
  }

  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>
        Time Range
      </Typography>
      <ButtonGroup size="small" variant="outlined">
        {PRESETS.map((preset) => (
          <Button
            key={preset.value}
            variant={timeRange.preset === preset.value ? 'contained' : 'outlined'}
            onClick={() => handlePresetClick(preset)}
          >
            {preset.label}
          </Button>
        ))}
      </ButtonGroup>
    </Box>
  )
}

export default TimeRangeSelector
