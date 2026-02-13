import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';
import { format } from 'date-fns';

export default function Forecasting() {
  const [metrics, setMetrics] = useState([]);
  const [selectedMetric, setSelectedMetric] = useState('');
  const [forecastDays, setForecastDays] = useState(7);
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    dashboardAPI.getMetrics()
      .then((data) => {
        setMetrics(data.metrics || []);
        if (data.metrics?.length) setSelectedMetric(data.metrics[0].name);
      })
      .catch(() => setMetrics([]));
  }, []);

  const handleForecast = () => {
    if (!selectedMetric) return;
    setLoading(true);
    setError(null);
    dashboardAPI.getForecast(selectedMetric, forecastDays, 'arima')
      .then(setForecastData)
      .catch((err) => {
        setError(err.message || 'Failed to generate forecast');
        setForecastData(null);
      })
      .finally(() => setLoading(false));
  };

  return (
    <div>
      <div className="controls">
        <div className="control-group">
          <label>Metric</label>
          <select value={selectedMetric} onChange={(e) => setSelectedMetric(e.target.value)}>
            {(metrics || []).map((m) => (
              <option key={m.name} value={m.name}>{m.display_name}</option>
            ))}
          </select>
        </div>
        <div className="control-group">
          <label>Days ahead</label>
          <input type="number" min={1} max={30} value={forecastDays} onChange={(e) => setForecastDays(Number(e.target.value))} />
        </div>
        <div className="control-group">
          <label>&nbsp;</label>
          <button className="btn btn-primary" onClick={handleForecast} disabled={loading}>
            {loading ? 'Generating...' : 'Generate forecast'}
          </button>
        </div>
      </div>

      {error && <div className="error">{error}</div>}
      {forecastData?.status === 'insufficient_data' && <div className="error">{forecastData.message}</div>}

      {forecastData?.predictions?.length > 0 && (
        <div className="chart-container">
          <div className="chart-header">
            <h3>Forecast: {forecastData.metric_name}</h3>
            <p>{forecastData.forecast_days} days · model: {forecastData.model_type}</p>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {forecastData.predictions.map((pred, i) => (
              <div key={i} className="forecast-item">
                <div className="forecast-date">{format(new Date(pred.date), 'MMM d, yyyy')}</div>
                <div className="forecast-value">{Number(pred.predicted_value).toFixed(2)}</div>
                <div className="forecast-confidence">
                  95% CI: [{Number(pred.confidence_lower).toFixed(2)}, {Number(pred.confidence_upper).toFixed(2)}]
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
