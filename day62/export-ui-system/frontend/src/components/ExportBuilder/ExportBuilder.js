import React, { useState } from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useDispatch } from 'react-redux';
import { createExport } from '../../redux/exportsSlice';
import FormatSelector from '../FormatSelector/FormatSelector';

const steps = ['Select Data', 'Choose Format', 'Configure Options'];

function ExportBuilder({ onComplete }) {
  const dispatch = useDispatch();
  const [activeStep, setActiveStep] = useState(0);
  const [config, setConfig] = useState({
    data_source: 'metrics',
    start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    end_date: new Date(),
    format_type: 'CSV',
    filters: {},
    fields: [],
    options: {},
  });

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSubmit = () => {
    const exportData = {
      user_id: 'demo-user',
      config: {
        ...config,
        start_date: config.start_date.toISOString(),
        end_date: config.end_date.toISOString(),
      },
    };

    dispatch(createExport(exportData));
    if (onComplete) onComplete();
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ mt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Data Source</InputLabel>
              <Select
                value={config.data_source}
                label="Data Source"
                onChange={(e) => setConfig({ ...config, data_source: e.target.value })}
              >
                <MenuItem value="metrics">Metrics Data</MenuItem>
                <MenuItem value="logs">Log Data</MenuItem>
                <MenuItem value="events">Event Data</MenuItem>
              </Select>
            </FormControl>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Start Date"
                value={config.start_date}
                onChange={(date) => setConfig({ ...config, start_date: date })}
                slotProps={{ textField: { fullWidth: true, sx: { mb: 2 } } }}
              />
              <DatePicker
                label="End Date"
                value={config.end_date}
                onChange={(date) => setConfig({ ...config, end_date: date })}
                slotProps={{ textField: { fullWidth: true } }}
              />
            </LocalizationProvider>
          </Box>
        );
      case 1:
        return (
          <FormatSelector
            selected={config.format_type}
            onSelect={(format) => setConfig({ ...config, format_type: format })}
          />
        );
      case 2:
        return (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Review Configuration
            </Typography>
            <Typography>Data Source: {config.data_source}</Typography>
            <Typography>Date Range: {config.start_date.toLocaleDateString()} - {config.end_date.toLocaleDateString()}</Typography>
            <Typography>Format: {config.format_type}</Typography>
          </Box>
        );
      default:
        return null;
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Create Export
      </Typography>
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      {renderStepContent(activeStep)}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
        <Button disabled={activeStep === 0} onClick={handleBack}>
          Back
        </Button>
        {activeStep === steps.length - 1 ? (
          <Button variant="contained" onClick={handleSubmit}>
            Create Export
          </Button>
        ) : (
          <Button variant="contained" onClick={handleNext}>
            Next
          </Button>
        )}
      </Box>
    </Paper>
  );
}

export default ExportBuilder;
