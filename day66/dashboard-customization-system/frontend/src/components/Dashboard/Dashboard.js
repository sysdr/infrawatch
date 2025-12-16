import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import GridLayout from 'react-grid-layout';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Menu,
  MenuItem
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SaveIcon from '@mui/icons-material/Save';
import ShareIcon from '@mui/icons-material/Share';
import SettingsIcon from '@mui/icons-material/Settings';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import { dashboardApi } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { useWebSocket } from '../../hooks/useWebSocket';
import WidgetFactory from '../Widgets/WidgetFactory';
import WidgetConfigPanel from '../Configuration/WidgetConfigPanel';
import ThemeSelector from '../Theme/ThemeSelector';
import ShareDialog from '../Sharing/ShareDialog';
import { useTheme } from '../../contexts/ThemeContext';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const Dashboard = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { currentTheme, setCurrentTheme } = useTheme();
  const [dashboard, setDashboard] = useState(null);
  const [layout, setLayout] = useState([]);
  const [widgets, setWidgets] = useState([]);
  const [configPanel, setConfigPanel] = useState({ open: false, widget: null });
  const [shareDialog, setShareDialog] = useState(false);
  const [menuAnchor, setMenuAnchor] = useState(null);
  
  const { connected, activeUsers, emitWidgetUpdate, emitThemeChange } = useWebSocket(id, user?.id);

  useEffect(() => {
    if (id) {
      loadDashboard();
    }
  }, [id]);

  const loadDashboard = async () => {
    try {
      const response = await dashboardApi.get(id);
      const data = response.data;
      setDashboard(data);
      setWidgets(data.config.layout || []);
      setCurrentTheme(data.theme || 'light');
      
      const gridLayout = (data.config.layout || []).map(w => ({
        i: w.widget_id,
        x: w.position[0],
        y: w.position[1],
        w: w.position[2],
        h: w.position[3]
      }));
      setLayout(gridLayout);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
      if (error.response?.status === 404) {
        // Dashboard not found, redirect to dashboard list
        alert('Dashboard not found. Redirecting to dashboard list.');
        navigate('/');
      }
    }
  };

  const handleLayoutChange = (newLayout) => {
    setLayout(newLayout);
    
    const updatedWidgets = widgets.map(widget => {
      const layoutItem = newLayout.find(l => l.i === widget.widget_id);
      if (layoutItem) {
        return {
          ...widget,
          position: [layoutItem.x, layoutItem.y, layoutItem.w, layoutItem.h]
        };
      }
      return widget;
    });
    
    setWidgets(updatedWidgets);
  };

  const handleSave = async () => {
    try {
      await dashboardApi.update(id, {
        config: {
          layout: widgets,
          metadata: dashboard.config.metadata || {}
        },
        theme: currentTheme,
        version: dashboard.version
      });
      alert('Dashboard saved successfully!');
      loadDashboard();
    } catch (error) {
      console.error('Failed to save dashboard:', error);
      alert('Failed to save dashboard. Please try again.');
    }
  };

  const handleAddWidget = (widgetType) => {
    const newWidget = {
      widget_id: `w${Date.now()}`,
      widget_type: widgetType,
      position: [0, widgets.length * 3, 4, 3],
      config: { 
        title: `New ${widgetType}`, 
        refreshInterval: 5000, // 5 seconds for demo visibility
        metric: widgetType === 'timeseries' ? 'cpu_usage' : undefined
      }
    };
    
    setWidgets([...widgets, newWidget]);
    setLayout([
      ...layout,
      {
        i: newWidget.widget_id,
        x: 0,
        y: widgets.length * 3,
        w: 4,
        h: 3
      }
    ]);
    setMenuAnchor(null);
  };

  const handleThemeChange = (theme) => {
    emitThemeChange(theme);
  };

  return (
    <Box sx={{ bgcolor: 'var(--background)', minHeight: '100vh' }}>
      <AppBar position="static" sx={{ bgcolor: 'var(--primary)' }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            {dashboard?.name || 'Dashboard'}
          </Typography>
          
          <Typography variant="body2" sx={{ mr: 2 }}>
            {connected ? `${activeUsers.length} user(s) online` : 'Offline'}
          </Typography>
          
          <ThemeSelector onThemeChange={handleThemeChange} />
          
          <IconButton color="inherit" onClick={(e) => setMenuAnchor(e.currentTarget)}>
            <AddIcon />
          </IconButton>
          <Menu
            anchorEl={menuAnchor}
            open={Boolean(menuAnchor)}
            onClose={() => setMenuAnchor(null)}
          >
            <MenuItem onClick={() => handleAddWidget('timeseries')}>Time Series Chart</MenuItem>
            <MenuItem onClick={() => handleAddWidget('metric')}>Metric Card</MenuItem>
          </Menu>
          
          <IconButton 
            color="inherit" 
            onClick={(e) => {
              e.currentTarget.blur();
              setShareDialog(true);
            }}
          >
            <ShareIcon />
          </IconButton>
          
          <Button color="inherit" startIcon={<SaveIcon />} onClick={handleSave}>
            Save
          </Button>
        </Toolbar>
      </AppBar>

      <Box sx={{ p: 3 }}>
        <GridLayout
          className="layout"
          layout={layout}
          cols={12}
          rowHeight={100}
          width={1200}
          onLayoutChange={handleLayoutChange}
          draggableHandle=".drag-handle"
        >
          {widgets.map((widget) => (
            <div key={widget.widget_id} style={{ position: 'relative' }}>
              <Box
                className="drag-handle"
                sx={{
                  position: 'absolute',
                  top: 8,
                  right: 8,
                  cursor: 'move',
                  zIndex: 1000
                }}
              >
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.currentTarget.blur();
                    setConfigPanel({ open: true, widget });
                  }}
                >
                  <SettingsIcon fontSize="small" />
                </IconButton>
              </Box>
              <WidgetFactory widget={widget} theme={currentTheme} />
            </div>
          ))}
        </GridLayout>
      </Box>

      <WidgetConfigPanel
        open={configPanel.open}
        widget={configPanel.widget}
        onClose={() => setConfigPanel({ open: false, widget: null })}
        onSave={(updatedWidget) => {
          setWidgets(widgets.map(w =>
            w.widget_id === updatedWidget.widget_id ? updatedWidget : w
          ));
        }}
      />

      <ShareDialog
        open={shareDialog}
        dashboardId={id}
        onClose={() => setShareDialog(false)}
      />
    </Box>
  );
};

export default Dashboard;
