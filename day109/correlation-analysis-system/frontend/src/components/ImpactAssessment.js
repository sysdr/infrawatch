import React, { useState, useEffect } from 'react';
import { Box, Button, CircularProgress, Chip } from '@mui/material';
import { Assessment } from '@mui/icons-material';
import apiService from '../services/apiService';

const ImpactAssessment = ({ rootCauses }) => {
  const [impact, setImpact] = useState(null);
  const [loading, setLoading] = useState(false);

  // Reset impact when root causes change (e.g. after new analysis) so user can pick again
  useEffect(() => {
    setImpact(null);
  }, [rootCauses]);

  const analyzeImpact = async (metricId) => {
    setLoading(true);
    try {
      const result = await apiService.analyzeImpact(metricId);
      setImpact(result);
    } catch (error) {
      console.error('Error analyzing impact:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!rootCauses || rootCauses.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height={400}>
        <div style={{ textAlign: 'center', color: '#999' }}>
          <p>No impact data available</p>
          <p style={{ fontSize: '0.9em' }}>Identify root causes first</p>
        </div>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height={400}>
        <CircularProgress />
      </Box>
    );
  }

  if (!impact) {
    return (
      <Box>
        <p style={{ marginBottom: 16, color: '#666' }}>
          Select a root cause to analyze its impact:
        </p>
        {rootCauses.slice(0, 5).map((cause, index) => (
          <Button
            key={index}
            variant="outlined"
            fullWidth
            onClick={() => analyzeImpact(cause.metric_id)}
            sx={{ mb: 1, justifyContent: 'flex-start' }}
            startIcon={<Assessment />}
          >
            {cause.metric_name}
          </Button>
        ))}
      </Box>
    );
  }

  const getSeverityColor = (severity) => {
    switch(severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 3, p: 2, background: '#f5f5f5', borderRadius: 2 }}>
        <div style={{ fontWeight: 600, marginBottom: 8 }}>
          Root Cause: {impact.root_metric_name}
        </div>
        <Box display="flex" gap={2}>
          <Chip 
            label={`${impact.impact_radius} Metrics`}
            color="primary"
            size="small"
          />
          <Chip 
            label={`${impact.total_services} Services`}
            color="secondary"
            size="small"
          />
        </Box>
      </Box>

      <div style={{ fontWeight: 600, marginBottom: 12 }}>
        Affected Metrics:
      </div>

      <Box sx={{ overflowY: 'auto', maxHeight: 300 }}>
        {impact.affected_metrics.slice(0, 10).map((metric, index) => (
          <Box
            key={index}
            sx={{
              p: 1.5,
              mb: 1,
              borderRadius: 2,
              background: 'rgba(255,255,255,0.7)',
              border: '1px solid #e0e0e0',
            }}
          >
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
              <div style={{ fontSize: '0.9em', fontWeight: 500 }}>
                {metric.metric_name}
              </div>
              <Chip 
                label={metric.severity}
                size="small"
                color={getSeverityColor(metric.severity)}
              />
            </Box>
            <Box display="flex" gap={1}>
              <Chip 
                label={`${(metric.probability * 100).toFixed(0)}%`}
                size="small"
                sx={{ fontSize: '0.7em' }}
              />
              <Chip 
                label={`Depth: ${metric.depth}`}
                size="small"
                sx={{ fontSize: '0.7em' }}
              />
              <Chip 
                label={metric.service}
                size="small"
                variant="outlined"
                sx={{ fontSize: '0.7em' }}
              />
            </Box>
          </Box>
        ))}
      </Box>

      <Button
        variant="text"
        fullWidth
        onClick={() => setImpact(null)}
        sx={{ mt: 2 }}
      >
        Analyze Different Root Cause
      </Button>
    </Box>
  );
};

export default ImpactAssessment;
