import React, { useState } from 'react';
import MetricsQuery from './components/MetricsQuery';
import MetricsChart from './components/MetricsChart';
import './App.css';

function App() {
  const [metricsData, setMetricsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentQuery, setCurrentQuery] = useState(null);

  const handleQuerySubmit = async (queryParams) => {
    setLoading(true);
    setError(null);
    setCurrentQuery(queryParams);

    try {
      const params = new URLSearchParams({
        metric_name: queryParams.metricName,
        start_time: queryParams.startTime,
        end_time: queryParams.endTime,
        interval: queryParams.interval,
        aggregations: queryParams.aggregation
      });

      const response = await fetch(`http://localhost:8000/api/v1/metrics/query?${params}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setMetricsData(data);
    } catch (err) {
      setError(err.message);
      console.error('Query failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Metrics API Dashboard
          </h1>
          <p className="text-gray-600">
            Day 26: Production-ready metrics querying with caching and aggregation
          </p>
        </header>

        <MetricsQuery 
          onQuerySubmit={handleQuerySubmit}
          loading={loading}
        />

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            <strong>Error:</strong> {error}
          </div>
        )}

        <MetricsChart 
          data={metricsData}
          metricName={currentQuery?.metricName}
          loading={loading}
          cacheHit={metricsData?.cache_hit}
        />

        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">API Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <strong>Query Endpoint:</strong><br />
              <code className="bg-gray-100 px-2 py-1 rounded">GET /api/v1/metrics/query</code>
            </div>
            <div>
              <strong>Export Endpoint:</strong><br />
              <code className="bg-gray-100 px-2 py-1 rounded">GET /api/v1/metrics/export</code>
            </div>
            <div>
              <strong>Supported Formats:</strong><br />
              JSON, CSV
            </div>
            <div>
              <strong>Caching:</strong><br />
              Redis with intelligent TTL
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
