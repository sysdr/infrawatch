import React, { useState, useCallback, useEffect, useRef } from 'react';
import GridLayout from 'react-grid-layout';
import { Box, IconButton, Typography } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { getWidgetComponent } from '../../utils/widgetRegistry';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const DashboardGrid = ({ widgets, layout, onLayoutChange, onWidgetRemove }) => {
  const containerRef = useRef(null);
  const [width, setWidth] = useState(1200);

  useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        setWidth(containerRef.current.offsetWidth);
      }
    };

    updateWidth();
    window.addEventListener('resize', updateWidth);
    return () => window.removeEventListener('resize', updateWidth);
  }, []);

  const handleLayoutChange = useCallback((newLayout) => {
    onLayoutChange(newLayout);
  }, [onLayoutChange]);

  if (widgets.length === 0) {
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '400px',
          flexDirection: 'column',
          gap: 2,
          color: '#64748b',
        }}
      >
        <Typography variant="h6" sx={{ color: '#1e293b', fontWeight: 600 }}>
          No widgets yet
        </Typography>
        <Typography variant="body2" sx={{ color: '#64748b', maxWidth: '400px', textAlign: 'center' }}>
          Click on a widget from the Widget Library to add it to your dashboard
        </Typography>
      </Box>
    );
  }

  return (
    <Box ref={containerRef} sx={{ position: 'relative', width: '100%' }}>
      <GridLayout
        className="layout"
        layout={layout}
        cols={24}
        rowHeight={30}
        width={width}
        onLayoutChange={handleLayoutChange}
        draggableHandle=".drag-handle"
        compactType="vertical"
        preventCollision={false}
        isDraggable={true}
        isResizable={true}
      >
        {widgets.map((widget) => {
          const WidgetComponent = getWidgetComponent(widget.widget_type);
          return (
            <div key={widget.id}>
              <Box
                sx={{
                  height: '100%',
                  width: '100%',
                  position: 'relative',
                  backgroundColor: 'white',
                  borderRadius: 3,
                  boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
                  border: '1px solid #e2e8f0',
                  overflow: 'hidden',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                    borderColor: '#10b981',
                  },
                  '&:hover .widget-controls': { opacity: 1 },
                }}
              >
                <Box
                  className="widget-controls"
                  sx={{
                    position: 'absolute',
                    top: 8,
                    right: 8,
                    zIndex: 10,
                    opacity: 0,
                    transition: 'opacity 0.2s',
                  }}
                >
                  <IconButton
                    size="small"
                    onClick={() => onWidgetRemove(widget.id)}
                    sx={{ bgcolor: 'background.paper', '&:hover': { bgcolor: 'error.main', color: 'white' } }}
                  >
                    <CloseIcon fontSize="small" />
                  </IconButton>
                </Box>
                <Box className="drag-handle" sx={{ height: '100%', cursor: 'move', p: 0 }}>
                  {WidgetComponent && <WidgetComponent config={widget.config} />}
                </Box>
              </Box>
            </div>
          );
        })}
      </GridLayout>
    </Box>
  );
};

export default DashboardGrid;
