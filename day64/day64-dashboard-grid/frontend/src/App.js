import React, { useState, useEffect, useCallback } from 'react';
import { Container, AppBar, Toolbar, Typography, Button, Box, Grid, Paper } from '@mui/material';
import DashboardGrid from './components/grid/DashboardGrid';
import WidgetLibrary from './components/grid/WidgetLibrary';
import TemplateSelector from './components/grid/TemplateSelector';
import { dashboardAPI, widgetAPI } from './services/api';
import { getWidgetConfig } from './utils/widgetRegistry';

function App() {
  const [dashboard, setDashboard] = useState(null);
  const [widgets, setWidgets] = useState([]);
  const [layout, setLayout] = useState([]);
  const [saveStatus, setSaveStatus] = useState('');

  useEffect(() => {
    initializeDashboard();
  }, []);

  const initializeDashboard = async () => {
    try {
      const dashboardsResponse = await dashboardAPI.getAll();
      let currentDashboard;

      if (dashboardsResponse.data.length > 0) {
        currentDashboard = dashboardsResponse.data[0];
      } else {
        const createResponse = await dashboardAPI.create({
          name: 'My Dashboard',
          description: 'Custom monitoring dashboard',
          layout: []
        });
        currentDashboard = createResponse.data;
      }

      setDashboard(currentDashboard);
      loadWidgets(currentDashboard.id);
    } catch (error) {
      console.error('Failed to initialize dashboard:', error);
    }
  };

  const loadWidgets = async (dashboardId) => {
    try {
      const response = await widgetAPI.getByDashboard(dashboardId);
      const loadedWidgets = response.data;
      setWidgets(loadedWidgets);

      const widgetLayout = loadedWidgets.map((widget) => ({
        i: widget.id,
        x: widget.position.x || 0,
        y: widget.position.y || 0,
        w: widget.position.w || 6,
        h: widget.position.h || 4,
        minW: getWidgetConfig(widget.widget_type)?.minW || 2,
        minH: getWidgetConfig(widget.widget_type)?.minH || 2,
      }));

      setLayout(widgetLayout);
    } catch (error) {
      console.error('Failed to load widgets:', error);
    }
  };

  const handleLayoutChange = useCallback((newLayout) => {
    setLayout(newLayout);
    
    if (dashboard) {
      const timeout = setTimeout(async () => {
        try {
          await dashboardAPI.update(dashboard.id, { layout: newLayout });
          
          for (const layoutItem of newLayout) {
            const widget = widgets.find((w) => w.id === layoutItem.i);
            if (widget) {
              await widgetAPI.update(widget.id, {
                position: {
                  x: layoutItem.x,
                  y: layoutItem.y,
                  w: layoutItem.w,
                  h: layoutItem.h,
                },
              });
            }
          }
          
          setSaveStatus('Saved');
          setTimeout(() => setSaveStatus(''), 2000);
        } catch (error) {
          console.error('Failed to save layout:', error);
        }
      }, 500);

      return () => clearTimeout(timeout);
    }
  }, [dashboard, widgets]);

  const handleWidgetAdd = async (widgetType) => {
    if (!dashboard) return;

    try {
      const widgetConfig = getWidgetConfig(widgetType);
      const newWidget = {
        dashboard_id: dashboard.id,
        widget_type: widgetType,
        title: widgetConfig.name,
        config: widgetConfig.defaultConfig,
        position: {
          x: 0,
          y: Infinity,
          w: widgetConfig.defaultW,
          h: widgetConfig.defaultH,
        },
      };

      const response = await widgetAPI.create(newWidget);
      const createdWidget = response.data;

      setWidgets((prev) => [...prev, createdWidget]);
      setLayout((prev) => [
        ...prev,
        {
          i: createdWidget.id,
          x: 0,
          y: Infinity,
          w: widgetConfig.defaultW,
          h: widgetConfig.defaultH,
          minW: widgetConfig.minW,
          minH: widgetConfig.minH,
        },
      ]);
    } catch (error) {
      console.error('Failed to add widget:', error);
    }
  };

  const handleWidgetRemove = async (widgetId) => {
    try {
      await widgetAPI.delete(widgetId);
      setWidgets((prev) => prev.filter((w) => w.id !== widgetId));
      setLayout((prev) => prev.filter((l) => l.i !== widgetId));
    } catch (error) {
      console.error('Failed to remove widget:', error);
    }
  };

  const handleTemplateApply = () => {
    if (dashboard) {
      loadWidgets(dashboard.id);
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" elevation={0}>
        <Toolbar sx={{ py: 1 }}>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            Dashboard Grid System
          </Typography>
          {saveStatus && (
            <Typography 
              variant="body2" 
              sx={{ 
                mr: 2, 
                color: '#10b981',
                fontWeight: 500,
                px: 1.5,
                py: 0.5,
                borderRadius: 1,
                bgcolor: 'rgba(255, 255, 255, 0.2)',
              }}
            >
              ✓ {saveStatus}
            </Typography>
          )}
          <Typography variant="body2" sx={{ fontWeight: 500, opacity: 0.95 }}>
            {dashboard?.name || 'Loading...'}
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={9}>
            <Paper 
              sx={{ 
                p: 3, 
                minHeight: '600px',
                bgcolor: '#ffffff',
                borderRadius: 3,
                border: '1px solid #e2e8f0',
              }}
            >
              {dashboard && (
                <DashboardGrid
                  widgets={widgets}
                  layout={layout}
                  onLayoutChange={handleLayoutChange}
                  onWidgetRemove={handleWidgetRemove}
                />
              )}
            </Paper>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
              <WidgetLibrary onWidgetAdd={handleWidgetAdd} />
              {dashboard && (
                <TemplateSelector
                  dashboardId={dashboard.id}
                  onTemplateApply={handleTemplateApply}
                />
              )}
            </Box>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}

export default App;
