import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Paper, Typography, Box, Breadcrumbs, Link, CircularProgress,
  Alert, Table, TableBody, TableCell, TableContainer, TableHead,
  TableRow, Button
} from '@mui/material';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import { analyticsApi } from '../api/analyticsClient';

function DrillDownExplorer() {
  const [level, setLevel] = useState(0);
  const [dimension, setDimension] = useState('channel');
  const [filters, setFilters] = useState({});
  const [breadcrumbs, setBreadcrumbs] = useState([{ level: 0, dimension: 'channel', filters: {} }]);

  const { data, isLoading, error } = useQuery({
    queryKey: ['drilldown', level, dimension, filters],
    queryFn: () => analyticsApi.drillDown(level, dimension, filters, 7),
  });

  const handleDrillDown = (nextDimension, filterKey, filterValue) => {
    const newFilters = { ...filters, [filterKey]: filterValue };
    const newLevel = level + 1;
    
    setLevel(newLevel);
    setDimension(nextDimension);
    setFilters(newFilters);
    setBreadcrumbs([...breadcrumbs, { level: newLevel, dimension: nextDimension, filters: newFilters }]);
  };

  const handleBreadcrumbClick = (index) => {
    const crumb = breadcrumbs[index];
    setLevel(crumb.level);
    setDimension(crumb.dimension);
    setFilters(crumb.filters);
    setBreadcrumbs(breadcrumbs.slice(0, index + 1));
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">Error loading drill-down data: {error.message}</Alert>;
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Box mb={3}>
        <Typography variant="h6" gutterBottom>Drill-Down Explorer</Typography>
        <Breadcrumbs separator={<NavigateNextIcon fontSize="small" />}>
          {breadcrumbs.map((crumb, index) => (
            <Link
              key={index}
              component="button"
              variant="body1"
              onClick={() => handleBreadcrumbClick(index)}
              sx={{
                cursor: 'pointer',
                textDecoration: index === breadcrumbs.length - 1 ? 'none' : 'underline',
                color: index === breadcrumbs.length - 1 ? 'text.primary' : 'primary.main',
              }}
            >
              {crumb.dimension}
            </Link>
          ))}
        </Breadcrumbs>
      </Box>

      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>{dimension}</strong></TableCell>
              <TableCell align="right"><strong>Count</strong></TableCell>
              {data?.can_drill_down && <TableCell align="right"><strong>Actions</strong></TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {data?.data?.map((row, index) => (
              <TableRow key={index} hover>
                <TableCell>{row[dimension] || 'N/A'}</TableCell>
                <TableCell align="right">{row.value?.toFixed(0) || 0}</TableCell>
                {data?.can_drill_down && (
                  <TableCell align="right">
                    {data.next_dimensions?.map(nextDim => (
                      <Button
                        key={nextDim}
                        size="small"
                        onClick={() => handleDrillDown(nextDim, dimension, row[dimension])}
                        sx={{ mr: 1 }}
                      >
                        View {nextDim}
                      </Button>
                    ))}
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {data?.data?.length === 0 && (
        <Box textAlign="center" py={4}>
          <Typography color="text.secondary">No data available</Typography>
        </Box>
      )}
    </Paper>
  );
}

export default DrillDownExplorer;
