import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { format } from 'date-fns';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function LogSearchInterface() {
  const [query, setQuery] = useState('');
  const [service, setService] = useState('');
  const [level, setLevel] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchDuration, setSearchDuration] = useState(null);
  const [totalResults, setTotalResults] = useState(0);

  const handleSearch = async () => {
    setLoading(true);

    try {
      const params = {};
      if (query) params.query = query;
      if (service) params.service = service;
      if (level) params.level = level;
      params.limit = 100;

      const response = await axios.get(`${API_BASE_URL}/api/logs/search`, { params });

      setResults(response.data.logs);
      setTotalResults(response.data.total);
      setSearchDuration(response.data.search_duration_ms);
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const getLevelColor = (level) => {
    const colors = {
      DEBUG: 'default',
      INFO: 'info',
      WARN: 'warning',
      ERROR: 'error',
      FATAL: 'error'
    };
    return colors[level] || 'default';
  };

  return (
    <Box>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>Search Logs</Typography>

        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            fullWidth
            size="small"
            label="Search query"
            placeholder="Search in message and service..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />

          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Service</InputLabel>
            <Select
              value={service}
              label="Service"
              onChange={(e) => setService(e.target.value)}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="auth-api">auth-api</MenuItem>
              <MenuItem value="user-service">user-service</MenuItem>
              <MenuItem value="payment-service">payment-service</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Level</InputLabel>
            <Select
              value={level}
              label="Level"
              onChange={(e) => setLevel(e.target.value)}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="DEBUG">DEBUG</MenuItem>
              <MenuItem value="INFO">INFO</MenuItem>
              <MenuItem value="WARN">WARN</MenuItem>
              <MenuItem value="ERROR">ERROR</MenuItem>
              <MenuItem value="FATAL">FATAL</MenuItem>
            </Select>
          </FormControl>

          <Button
            variant="contained"
            startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
            onClick={handleSearch}
            disabled={loading}
          >
            Search
          </Button>
        </Box>

        {searchDuration !== null && (
          <Typography variant="body2" color="textSecondary">
            Found {totalResults} results in {searchDuration.toFixed(0)}ms
          </Typography>
        )}
      </Paper>

      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Timestamp</TableCell>
              <TableCell>Level</TableCell>
              <TableCell>Service</TableCell>
              <TableCell>Message</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : results.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  No results found
                </TableCell>
              </TableRow>
            ) : (
              results.map((log, index) => (
                <TableRow key={index} hover>
                  <TableCell>
                    {log.timestamp ? format(new Date(log.timestamp), 'yyyy-MM-dd HH:mm:ss') : 'N/A'}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={log.level}
                      color={getLevelColor(log.level)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{log.service}</TableCell>
                  <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                    {log.message}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default LogSearchInterface;
