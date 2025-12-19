import React, { useState, useEffect, useMemo } from 'react';
import { FixedSizeGrid as Grid } from 'react-window';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import ChartWidget from '../charts/ChartWidget';
import { dashboardAPI } from '../../services/api';
import { getCachedData, setCachedData } from '../../services/indexedDBService';

const WIDGET_WIDTH = 400;
const WIDGET_HEIGHT = 350;
const GAP = 16;

function DashboardGrid({ widgetCount, realtimeMetrics }) {
  const [widgets, setWidgets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [containerWidth, setContainerWidth] = useState(window.innerWidth - 48);

  const columnsCount = Math.floor(containerWidth / (WIDGET_WIDTH + GAP));
  const rowsCount = Math.ceil(widgetCount / columnsCount);

  useEffect(() => {
    loadWidgets();
    
    const handleResize = () => {
      setContainerWidth(window.innerWidth - 48);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [widgetCount]);

  const loadWidgets = async () => {
    setLoading(true);
    try {
      // Check IndexedDB first
      const cached = await getCachedData(`widgets_${widgetCount}`);
      
      if (cached && (Date.now() - cached.timestamp < 300000)) {
        setWidgets(cached.data);
        setLoading(false);
        return;
      }

      // Fetch from API
      const response = await dashboardAPI.getWidgets(widgetCount);
      setWidgets(response.widgets);
      
      // Cache in IndexedDB
      await setCachedData(`widgets_${widgetCount}`, response.widgets);
    } catch (error) {
      console.error('Error loading widgets:', error);
    } finally {
      setLoading(false);
    }
  };

  const Cell = ({ columnIndex, rowIndex, style }) => {
    const index = rowIndex * columnsCount + columnIndex;
    if (index >= widgets.length) return null;

    const widget = widgets[index];
    
    return (
      <div style={{
        ...style,
        padding: GAP / 2,
      }}>
        <ChartWidget 
          widget={widget} 
          realtimeUpdate={realtimeMetrics?.[widget.metric]}
        />
      </div>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', height: 'calc(100vh - 250px)' }}>
      <Grid
        columnCount={columnsCount}
        columnWidth={WIDGET_WIDTH + GAP}
        height={window.innerHeight - 250}
        rowCount={rowsCount}
        rowHeight={WIDGET_HEIGHT + GAP}
        width={containerWidth}
        overscanRowCount={1}
      >
        {Cell}
      </Grid>
    </Box>
  );
}

export default DashboardGrid;
