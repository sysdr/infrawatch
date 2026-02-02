/**
 * Sample data shown on dashboards when "Start Simulation" is clicked
 * and the backend returns no data (e.g. backend unreachable or fresh run).
 */

const now = new Date();
const iso = (d) => d.toISOString();

export const SAMPLE_PATTERNS = [
  { id: 1, template: 'User * logged in successfully from IP *', category: 'auth', severity: 'info', frequency: 42, is_critical: false, last_seen: iso(now) },
  { id: 2, template: 'API request processed in *ms', category: 'performance', severity: 'info', frequency: 128, is_critical: false, last_seen: iso(new Date(now - 60000)) },
  { id: 3, template: 'Database query executed successfully', category: 'database', severity: 'info', frequency: 89, is_critical: false, last_seen: iso(new Date(now - 120000)) },
  { id: 4, template: 'Failed to connect to database timeout after *s', category: 'database', severity: 'error', frequency: 5, is_critical: true, last_seen: iso(new Date(now - 180000)) },
  { id: 5, template: 'Authentication failed for user *', category: 'auth', severity: 'error', frequency: 12, is_critical: true, last_seen: iso(new Date(now - 240000)) },
  { id: 6, template: 'Critical service unavailable', category: 'system', severity: 'critical', frequency: 2, is_critical: true, last_seen: iso(new Date(now - 300000)) },
  { id: 7, template: 'Request processed', category: 'performance', severity: 'info', frequency: 256, is_critical: false, last_seen: iso(now) },
  { id: 8, template: 'Unusual traffic pattern detected', category: 'security', severity: 'warning', frequency: 8, is_critical: false, last_seen: iso(new Date(now - 90000)) },
];

export const SAMPLE_ANOMALIES = [
  { id: 1, timestamp: iso(now), metric_name: 'response_time', metric_value: 5000, z_score: 3.2, anomaly_type: 'zscore', severity: 'warning' },
  { id: 2, timestamp: iso(new Date(now - 120000)), metric_name: 'error_rate', metric_value: 25, z_score: 4.1, anomaly_type: 'zscore', severity: 'critical' },
  { id: 3, timestamp: iso(new Date(now - 240000)), metric_name: 'response_time', metric_value: 3456, z_score: 2.8, anomaly_type: 'zscore', severity: 'warning' },
  { id: 4, timestamp: iso(new Date(now - 360000)), metric_name: 'error_rate', metric_value: 18, z_score: 2.5, anomaly_type: 'zscore', severity: 'warning' },
];

export const SAMPLE_TRENDS = [
  { metric_name: 'response_time', trend_direction: 'up', moving_average: 156.4, predicted_value_1h: 172.1, confidence_interval: 12.3 },
  { metric_name: 'error_rate', trend_direction: 'up', moving_average: 8.2, predicted_value_1h: 11.5, confidence_interval: 2.1 },
  { metric_name: 'request_count', trend_direction: 'stable', moving_average: 1200, predicted_value_1h: 1180, confidence_interval: 80 },
];

export const SAMPLE_ALERTS = [
  { id: 1, timestamp: iso(now), title: 'High error rate detected in simulator', alert_type: 'anomaly', severity: 'critical', status: 'active' },
  { id: 2, timestamp: iso(new Date(now - 60000)), title: 'Response time spike', alert_type: 'pattern', severity: 'warning', status: 'active' },
  { id: 3, timestamp: iso(new Date(now - 300000)), title: 'Anomaly detected in response_time', alert_type: 'anomaly', severity: 'warning', status: 'acknowledged' },
  { id: 4, timestamp: iso(new Date(now - 600000)), title: 'Frequency spike for pattern', alert_type: 'pattern', severity: 'info', status: 'resolved' },
];

export const SAMPLE_ALERT_STATS = {
  total: 12,
  active: 2,
  resolved: 8,
  by_severity: { critical: 1, warning: 2, info: 1 },
};
