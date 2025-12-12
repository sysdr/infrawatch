import CPUChart from '../components/widgets/CPUChart';
import MemoryGauge from '../components/widgets/MemoryGauge';
import AlertList from '../components/widgets/AlertList';
import MetricCard from '../components/widgets/MetricCard';

export const widgetRegistry = {
  cpu_chart: {
    component: CPUChart,
    name: 'CPU Usage Chart',
    description: 'Real-time CPU utilization chart',
    defaultConfig: { refreshInterval: 5000 },
    minW: 3,
    minH: 2,
    defaultW: 6,
    defaultH: 4,
  },
  memory_gauge: {
    component: MemoryGauge,
    name: 'Memory Gauge',
    description: 'Memory usage gauge visualization',
    defaultConfig: { threshold: 80 },
    minW: 2,
    minH: 2,
    defaultW: 3,
    defaultH: 3,
  },
  alert_list: {
    component: AlertList,
    name: 'Alert List',
    description: 'Recent alerts and notifications',
    defaultConfig: { limit: 10 },
    minW: 4,
    minH: 3,
    defaultW: 6,
    defaultH: 4,
  },
  metric_card: {
    component: MetricCard,
    name: 'Metric Card',
    description: 'Single metric display card',
    defaultConfig: { metric: 'requests_per_second' },
    minW: 2,
    minH: 2,
    defaultW: 3,
    defaultH: 2,
  },
};

export const getWidgetComponent = (type) => {
  const widget = widgetRegistry[type];
  return widget ? widget.component : null;
};

export const getWidgetConfig = (type) => {
  return widgetRegistry[type] || null;
};
