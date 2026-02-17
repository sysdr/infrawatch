import React from 'react';
import { Box, Chip, LinearProgress } from '@mui/material';
import { TrendingUp } from '@mui/icons-material';

const RootCausePanel = ({ rootCauses }) => {
  if (!rootCauses || rootCauses.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height={300}>
        <div style={{ textAlign: 'center', color: '#999' }}>
          <p>No root causes identified</p>
          <p style={{ fontSize: '0.9em' }}>Run root cause analysis to see results</p>
        </div>
      </Box>
    );
  }

  const maxScore = Math.max(...rootCauses.map(rc => rc.root_score));

  return (
    <Box sx={{ overflowY: 'auto', maxHeight: 350 }}>
      {rootCauses.map((cause, index) => (
        <Box
          key={index}
          sx={{
            p: 2,
            mb: 2,
            borderRadius: 2,
            background: 'linear-gradient(135deg, #667eea20 0%, #764ba220 100%)',
            border: '2px solid',
            borderColor: index === 0 ? '#f5576c' : '#e0e0e0',
            transition: 'all 0.2s',
            '&:hover': {
              transform: 'scale(1.02)',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            }
          }}
        >
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
            <div style={{ fontWeight: 600, fontSize: '0.95em' }}>
              {cause.metric_name}
            </div>
            {index === 0 && (
              <Chip 
                icon={<TrendingUp />}
                label="Primary" 
                size="small" 
                color="error"
              />
            )}
          </Box>
          
          <Box display="flex" gap={2} mb={1}>
            <Chip 
              label={`↗ ${cause.outgoing_effects}`}
              size="small"
              sx={{ 
                background: '#43e97b20',
                color: '#2e7d32',
                fontWeight: 600 
              }}
            />
            <Chip 
              label={`↙ ${cause.incoming_causes}`}
              size="small"
              sx={{ 
                background: '#4facfe20',
                color: '#1976d2',
                fontWeight: 600 
              }}
            />
          </Box>

          <Box>
            <div style={{ 
              fontSize: '0.75em', 
              color: '#666',
              marginBottom: 4 
            }}>
              Root Score: {cause.root_score.toFixed(2)}
            </div>
            <LinearProgress 
              variant="determinate" 
              value={(cause.root_score / maxScore) * 100}
              sx={{
                height: 6,
                borderRadius: 1,
                background: '#e0e0e0',
                '& .MuiLinearProgress-bar': {
                  background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                }
              }}
            />
          </Box>
        </Box>
      ))}
    </Box>
  );
};

export default RootCausePanel;
