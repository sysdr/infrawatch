import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';
import { format } from 'date-fns';

const formatValue = (value, unit) => {
  if (value === null || value === undefined) return 'N/A';
  if (unit === 'USD') return `$${Number(value).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
  if (unit === '%') return `${Number(value).toFixed(2)}%`;
  if (unit === 'ms') return `${Number(value).toFixed(0)}ms`;
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 });
};

export default function KPIDashboard() {
  const [kpis, setKpis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchKPIs = async () => {
    try {
      setLoading(true);
      const data = await dashboardAPI.getKPIs();
      setKpis(data.kpis || []);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      setError('Failed to fetch KPIs. Ensure backend is running and data is seeded.');
      setKpis([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchKPIs(); const id = setInterval(fetchKPIs, 30000); return () => clearInterval(id); }, []);

  if (loading && kpis.length === 0) return <div className="loading">Loading dashboard...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div>
      <div className="kpi-grid">
        {kpis.map((kpi) => (
          <div key={kpi.metric_name} className="kpi-card">
            <div className="kpi-title">{kpi.display_name}</div>
            <div className={`trend-indicator trend-${(kpi.trend || 'stable').toLowerCase()}`} style={{ marginTop: 4 }}>{kpi.trend || '—'}</div>
            <div className="kpi-value">{formatValue(kpi.current_value, kpi.unit)}</div>
            {kpi.change_percentage != null && (
              <div style={{ color: kpi.change_percentage >= 0 ? '#10b981' : '#ef4444', fontSize: '0.875rem' }}>
                {(kpi.change_percentage >= 0 ? '+' : '') + Number(kpi.change_percentage).toFixed(2)}% vs previous period
              </div>
            )}
            <div style={{ marginTop: 8, fontSize: '0.875rem', color: '#657786' }}>
              Target: {formatValue(kpi.target_value, kpi.unit)} · {kpi.data_points ?? 0} points
            </div>
          </div>
        ))}
      </div>
      {lastUpdated && <div style={{ textAlign: 'center', color: '#657786', fontSize: '0.875rem' }}>Last updated: {format(lastUpdated, 'HH:mm:ss')}</div>}
    </div>
  );
}
