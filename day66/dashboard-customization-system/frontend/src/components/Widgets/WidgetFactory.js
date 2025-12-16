import React from 'react';
import TimeSeriesWidget from './TimeSeriesWidget';
import MetricWidget from './MetricWidget';

const WidgetFactory = ({ widget, theme }) => {
  const widgetComponents = {
    timeseries: TimeSeriesWidget,
    metric: MetricWidget
  };

  const WidgetComponent = widgetComponents[widget.widget_type] || (() => <div>Unknown widget type</div>);
  
  return <WidgetComponent config={widget.config} theme={theme} />;
};

export default WidgetFactory;
