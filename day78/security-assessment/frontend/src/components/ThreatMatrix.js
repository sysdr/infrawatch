import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  Grid,
  Chip,
} from '@mui/material';
import { securityAPI } from '../services/api';

const ThreatMatrix = () => {
  const [threats, setThreats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadThreats();

    // Periodically refresh so STRIDE cards stay up to date after scans
    const intervalId = setInterval(loadThreats, 15000);
    return () => clearInterval(intervalId);
  }, []);

  const loadThreats = async () => {
    try {
      setLoading(true);
      const response = await securityAPI.getThreatModel();
      setThreats(response.data.threats);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load threats:', error);
      setLoading(false);
    }
  };

  const getRiskColor = (riskScore) => {
    if (riskScore >= 15) return '#d32f2f';
    if (riskScore >= 8) return '#f57c00';
    return '#388e3c';
  };

  const strideCategories = ['Spoofing', 'Tampering', 'Repudiation', 'Information Disclosure', 'Denial of Service', 'Elevation of Privilege'];

  const getThreatsByCategory = (category) => {
    return threats.filter(t => t.category === category);
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        STRIDE Threat Model
      </Typography>
      {loading && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Updating threat data...
        </Typography>
      )}

      <Grid container spacing={2}>
        {strideCategories.map((category) => {
          const categoryThreats = getThreatsByCategory(category);
          const maxRisk = categoryThreats.length > 0 
            ? Math.max(...categoryThreats.map(t => t.risk_score))
            : 0;

          return (
            <Grid item xs={12} sm={6} key={category}>
              <Box
                sx={{
                  p: 2,
                  border: '2px solid',
                  borderColor: getRiskColor(maxRisk),
                  borderRadius: 2,
                  bgcolor: `${getRiskColor(maxRisk)}10`,
                  height: '100%'
                }}
              >
                <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                  {category}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {categoryThreats.length} threats identified
                </Typography>
                {categoryThreats.length > 0 && (
                  <Box mt={1}>
                    <Chip
                      label={`Max Risk: ${maxRisk}`}
                      size="small"
                      sx={{
                        bgcolor: getRiskColor(maxRisk),
                        color: 'white'
                      }}
                    />
                  </Box>
                )}
              </Box>
            </Grid>
          );
        })}
      </Grid>

      <Box mt={3}>
        <Typography variant="subtitle2" gutterBottom>
          Top Threats
        </Typography>
        {threats.slice(0, 5).map((threat, idx) => (
          <Box
            key={threat.id}
            sx={{
              p: 2,
              mb: 1,
              border: '1px solid #e0e0e0',
              borderRadius: 1,
              borderLeft: `4px solid ${getRiskColor(threat.risk_score)}`
            }}
          >
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="body2" fontWeight="500">
                {threat.component}
              </Typography>
              <Chip
                label={`Risk: ${threat.risk_score}`}
                size="small"
                sx={{
                  bgcolor: getRiskColor(threat.risk_score),
                  color: 'white'
                }}
              />
            </Box>
            <Typography variant="caption" color="text.secondary">
              {threat.description}
            </Typography>
          </Box>
        ))}
      </Box>
    </Paper>
  );
};

export default ThreatMatrix;
