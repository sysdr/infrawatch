import React, { useState, useEffect } from 'react';
import { BarChart3, Activity } from 'lucide-react';
import MetricLineChart from '../charts/LineChart';
import TimeRangeSelector from '../controls/TimeRangeSelector';
import MetricSelector from '../controls/MetricSelector';
import { useMetrics } from '../../hooks/useMetrics';

const Dashboard = () => {
  const [selectedMetrics, setSelectedMetrics] = useState(['cpu_usage', 'memory_usage']);
  const [timeRange, setTimeRange] = useState('1h');

  const handleMetricToggle = (metricName) => {
    setSelectedMetrics(prev => 
      prev.includes(metricName)
        ? prev.filter(m => m !== metricName)
        : [...prev, metricName]
    );
  };

  return (
    <div className="min-h-screen bg-wp-gray-light">
      {/* Header */}
      <header className="wp-header">
        <div className="flex items-center gap-3">
          <BarChart3 size={24} />
          <h1 className="text-xl font-semibold">Metrics Dashboard</h1>
          <div className="ml-auto flex items-center gap-2">
            <Activity size={16} className="text-green-400" />
            <span className="text-sm">Live</span>
          </div>
        </div>
      </header>

      <div className="container mx-auto p-6">
        {/* Controls Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <TimeRangeSelector 
            selectedRange={timeRange}
            onRangeChange={setTimeRange}
          />
          <MetricSelector
            selectedMetrics={selectedMetrics}
            onMetricToggle={handleMetricToggle}
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {selectedMetrics.map((metricName, index) => (
            <ChartContainer
              key={metricName}
              metricName={metricName}
              timeRange={timeRange}
              color={getChartColor(index)}
            />
          ))}
        </div>

        {selectedMetrics.length === 0 && (
          <div className="wp-card text-center py-12">
            <BarChart3 size={48} className="mx-auto mb-4 text-wp-gray" />
            <h3 className="text-lg font-medium text-wp-gray mb-2">No Metrics Selected</h3>
            <p className="text-wp-gray">Select metrics from the control panel to view charts</p>
          </div>
        )}
      </div>
    </div>
  );
};

const ChartContainer = ({ metricName, timeRange, color }) => {
  const { data, loading, error } = useMetrics(metricName, timeRange);

  if (loading) {
    return (
      <div className="wp-card h-80 flex items-center justify-center">
        <div className="text-wp-gray">Loading {metricName} data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="wp-card h-80 flex items-center justify-center">
        <div className="text-red-600">Error loading {metricName}: {error}</div>
      </div>
    );
  }

  return (
    <MetricLineChart
      data={data}
      metricName={metricName}
      color={color}
    />
  );
};

const getChartColor = (index) => {
  const colors = ['#0073aa', '#00a32a', '#ff6900', '#d63638', '#8b5cf6', '#06b6d4'];
  return colors[index % colors.length];
};

export default Dashboard;
