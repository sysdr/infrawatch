import React, { useState } from 'react';
import { Paper, Typography, Box, TextField, Button, Chip, Alert } from '@mui/material';
import { invalidateCache } from '../services/api';

export default function CachePanel({ data }) {
  const [tag, setTag] = useState('');
  const [result, setResult] = useState(null);

  const bust = async () => {
    if (!tag.trim()) return;
    try {
      const r = await invalidateCache(tag.trim());
      setResult({ ok: true, msg: `Busted ${r.deleted_keys} keys for tag "${r.tag}"` });
    } catch {
      setResult({ ok: false, msg: 'Invalidation failed — is the backend running?' });
    }
  };

  if (!data) return null;
  const hitRate = data.cache.hit_rate_pct;
  const color = hitRate >= 85 ? '#2e7d32' : hitRate >= 60 ? '#f57f17' : '#c62828';

  return (
    <Paper elevation={0} sx={{ p: 2.5, borderRadius: 3, border: '1px solid #e8f5e9' }}>
      <Typography variant="subtitle2" fontWeight={700} color="#2e7d32" gutterBottom>
        Redis Cache
      </Typography>
      <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
        <Chip label={`Hits: ${data.cache.hits}`} size="small" sx={{ bgcolor: '#e8f5e9', color: '#1b5e20' }} />
        <Chip label={`Misses: ${data.cache.misses}`} size="small" sx={{ bgcolor: '#fafafa', color: '#555' }} />
        <Chip label={`Hit Rate: ${hitRate}%`} size="small"
          sx={{ bgcolor: color, color: 'white', fontWeight: 700 }} />
      </Box>
      <Box display="flex" gap={1} alignItems="center">
        <TextField size="small" value={tag} onChange={e => setTag(e.target.value)}
          placeholder="e.g. team:abc" label="Invalidation Tag"
          sx={{ flex: 1, '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
        <Button variant="contained" size="small" onClick={bust}
          sx={{ bgcolor: '#2e7d32', borderRadius: 2, textTransform: 'none',
            '&:hover': { bgcolor: '#1b5e20' } }}>
          Bust Cache
        </Button>
      </Box>
      {result && (
        <Alert severity={result.ok ? 'success' : 'error'}
          sx={{ mt: 1, py: 0.5, borderRadius: 2, fontSize: 12 }}>
          {result.msg}
        </Alert>
      )}
    </Paper>
  );
}
