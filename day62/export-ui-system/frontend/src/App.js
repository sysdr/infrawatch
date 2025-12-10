import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Tabs,
  Tab,
  AppBar,
  Toolbar,
  CssBaseline,
  ThemeProvider,
  createTheme,
} from '@mui/material';
import { Provider } from 'react-redux';
import { store } from './redux/store';
import ExportBuilder from './components/ExportBuilder/ExportBuilder';
import HistoryPanel from './components/HistoryPanel/HistoryPanel';
import ProgressTracker from './components/ProgressTracker/ProgressTracker';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2e7d32', // Professional green
      dark: '#1b5e20',
      light: '#4caf50',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#424242', // Dark gray
      dark: '#212121',
      light: '#616161',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
    text: {
      primary: '#212121',
      secondary: '#757575',
    },
    divider: '#e0e0e0',
    success: {
      main: '#2e7d32',
      light: '#4caf50',
      dark: '#1b5e20',
    },
    error: {
      main: '#c62828',
      light: '#ef5350',
      dark: '#b71c1c',
    },
    warning: {
      main: '#f57c00',
      light: '#ff9800',
      dark: '#e65100',
    },
    info: {
      main: '#616161',
      light: '#9e9e9e',
      dark: '#424242',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          background: 'linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        },
        elevation1: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: 8,
        },
        contained: {
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          '&:hover': {
            boxShadow: '0 4px 8px rgba(0,0,0,0.15)',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid #e0e0e0',
        },
        indicator: {
          backgroundColor: '#2e7d32',
          height: 3,
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          fontSize: '0.95rem',
          minHeight: 48,
          '&.Mui-selected': {
            color: '#2e7d32',
            fontWeight: 600,
          },
        },
      },
    },
    MuiStepper: {
      styleOverrides: {
        root: {
          '& .MuiStepLabel-label.Mui-completed': {
            color: '#2e7d32',
          },
          '& .MuiStepLabel-label.Mui-active': {
            color: '#2e7d32',
            fontWeight: 600,
          },
        },
      },
    },
    MuiStepIcon: {
      styleOverrides: {
        root: {
          '&.Mui-completed': {
            color: '#2e7d32',
          },
          '&.Mui-active': {
            color: '#2e7d32',
          },
        },
      },
    },
  },
});

function TabPanel({ children, value, index }) {
  return value === index ? <Box sx={{ py: 3 }}>{children}</Box> : null;
}

function App() {
  const [tabValue, setTabValue] = useState(0);

  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div">
              Export UI System
            </Typography>
          </Toolbar>
        </AppBar>
        <Container maxWidth="lg" sx={{ py: 4 }}>
          <Box sx={{ 
            borderBottom: 1, 
            borderColor: 'divider', 
            mb: 3,
            backgroundColor: 'background.paper',
            borderRadius: 2,
            px: 2,
            pt: 2
          }}>
            <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
              <Tab label="Create Export" />
              <Tab label="Export History" />
            </Tabs>
          </Box>
          <TabPanel value={tabValue} index={0}>
            <ExportBuilder onComplete={() => setTabValue(1)} />
          </TabPanel>
          <TabPanel value={tabValue} index={1}>
            <HistoryPanel />
          </TabPanel>
        </Container>
      </ThemeProvider>
    </Provider>
  );
}

export default App;
