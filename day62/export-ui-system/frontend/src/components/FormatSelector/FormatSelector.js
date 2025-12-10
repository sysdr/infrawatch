import React, { useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Radio,
  RadioGroup,
  FormControlLabel,
  Grid,
  Paper,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { fetchPreview } from '../../redux/exportsSlice';

const formats = [
  {
    value: 'CSV',
    title: 'CSV',
    description: 'Comma-separated values, Excel compatible',
    sizeMultiplier: '1x',
  },
  {
    value: 'JSON',
    title: 'JSON',
    description: 'Structured data format for developers',
    sizeMultiplier: '1.2x',
  },
  {
    value: 'EXCEL',
    title: 'Excel',
    description: 'Native Excel format with formatting',
    sizeMultiplier: '1.5x',
  },
  {
    value: 'PDF',
    title: 'PDF',
    description: 'Formatted report for presentations',
    sizeMultiplier: '3x',
  },
];

function FormatSelector({ selected, onSelect }) {
  const dispatch = useDispatch();
  const preview = useSelector((state) => state.exports.preview);

  useEffect(() => {
    if (selected) {
      dispatch(fetchPreview(selected));
    }
  }, [selected, dispatch]);

  return (
    <Box>
      <RadioGroup value={selected} onChange={(e) => onSelect(e.target.value)}>
        <Grid container spacing={2}>
          {formats.map((format) => (
            <Grid item xs={12} sm={6} key={format.value}>
              <Card
                variant="outlined"
                sx={{
                  cursor: 'pointer',
                  border: selected === format.value ? 2 : 1,
                  borderColor: selected === format.value ? 'primary.main' : 'divider',
                }}
                onClick={() => onSelect(format.value)}
              >
                <CardContent>
                  <FormControlLabel
                    value={format.value}
                    control={<Radio />}
                    label={
                      <Box>
                        <Typography variant="h6">{format.title}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {format.description}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Size: {format.sizeMultiplier}
                        </Typography>
                      </Box>
                    }
                  />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </RadioGroup>

      {preview && (
        <Paper sx={{ mt: 3, p: 2, maxHeight: 300, overflow: 'auto' }}>
          <Typography variant="h6" gutterBottom>
            Preview
          </Typography>
          <pre style={{ fontSize: '12px', margin: 0 }}>
            {preview.format === 'CSV' ? preview.preview : JSON.stringify(preview.data, null, 2)}
          </pre>
        </Paper>
      )}
    </Box>
  );
}

export default FormatSelector;
