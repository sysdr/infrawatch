import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { api } from './utils/api';
import { LatencyChart, ThroughputChart, ConnectionChart } from './components/Charts';
import { MetricCard } from './components/MetricCard';

function App() {
  const [metrics, setMetrics] = useState({
    connections: 0,
    total_messages: 0,
    errors: 0,
    p50_latency: 0,
    p95_latency: 0,
    p99_latency: 0,
    throughput: 0,
    cpu_percent: 0,
    memory_mb: 0
  });
  const [metricsHistory, setMetricsHistory] = useState([]);
  const [testResults, setTestResults] = useState([]);
  const [currentTest, setCurrentTest] = useState(null);
  const [isRunning, setIsRunning] = useState(false);

  const fetchMetrics = useCallback(async () => {
    try {
      const newMetrics = await api.get('/metrics');
      setMetrics(newMetrics);
      
      setMetricsHistory(prev => {
        const updated = [...prev, {
          time: new Date().toLocaleTimeString(),
          connections: newMetrics.connections,
          latency: newMetrics.p99_latency,
          throughput: newMetrics.throughput,
          errors: newMetrics.errors
        }];
        return updated.slice(-30);
      });
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  }, []);

  const fetchTestResults = useCallback(async () => {
    try {
      const data = await api.get('/tests');
      setTestResults(data);
    } catch (error) {
      console.error('Failed to fetch test results:', error);
    }
  }, []);

  const fetchCurrentTest = useCallback(async () => {
    try {
      const data = await api.get('/tests/current');
      setCurrentTest(data);
      const isTestRunning = data.status === 'running' || data.status === 'starting';
      setIsRunning(prev => {
        const wasRunning = prev;
        // If test completed, refresh test results
        if (data.status === 'completed' && wasRunning) {
          fetchTestResults();
        }
        return isTestRunning;
      });
    } catch (error) {
      console.error('Failed to fetch current test:', error);
    }
  }, [fetchTestResults]);

  useEffect(() => {
    // Initial load
    fetchMetrics();
    fetchTestResults();
    fetchCurrentTest();
    
    // Poll for updates (optimized: faster when test is running)
    const pollInterval = isRunning ? 500 : 2000;
    const interval = setInterval(() => {
      fetchMetrics();
      if (isRunning) {
        fetchCurrentTest();
      }
    }, pollInterval);
    
    return () => clearInterval(interval);
  }, [fetchMetrics, fetchTestResults, fetchCurrentTest, isRunning]);

  const startTest = async (testConfig) => {
    try {
      setIsRunning(true);
      await api.post('/tests/start', testConfig);
      // Immediately fetch to get updated status
      await fetchCurrentTest();
      await fetchMetrics();
    } catch (error) {
      console.error('Failed to start test:', error);
      setIsRunning(false);
    }
  };

  const stopTest = async () => {
    try {
      await api.post('/tests/stop', {});
      setIsRunning(false);
      await fetchTestResults();
      await fetchCurrentTest();
      await fetchMetrics();
    } catch (error) {
      console.error('Failed to stop test:', error);
    }
  };

  const resetMetrics = async () => {
    try {
      await api.post('/metrics/reset', {});
      setMetricsHistory([]);
    } catch (error) {
      console.error('Failed to reset metrics:', error);
    }
  };

  // Memoize expensive computations
  const latencyData = useMemo(() => [
    { name: 'P50', value: metrics.p50_latency, fill: '#10B981' },
    { name: 'P95', value: metrics.p95_latency, fill: '#F59E0B' },
    { name: 'P99', value: metrics.p99_latency, fill: '#EF4444' }
  ], [metrics.p50_latency, metrics.p95_latency, metrics.p99_latency]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                WebSocket Testing Dashboard
              </h1>
              <p className="text-sm text-gray-500">Real-time performance monitoring</p>
            </div>
            <div className="flex items-center gap-3">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                isRunning 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {isRunning ? '● Running' : '○ Idle'}
              </span>
              <button
                onClick={resetMetrics}
                className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition"
              >
                Reset
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Metrics Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <MetricCard 
            title="Connections" 
            value={metrics.connections} 
            color="blue"
          />
          <MetricCard 
            title="Messages" 
            value={metrics.total_messages} 
            color="green"
          />
          <MetricCard 
            title="Throughput" 
            value={`${metrics.throughput?.toFixed(0) || 0}/s`} 
            color="purple"
          />
          <MetricCard 
            title="Errors" 
            value={metrics.errors} 
            color={metrics.errors > 0 ? "red" : "gray"}
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Latency Distribution */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4">Latency Distribution (ms)</h3>
            <LatencyChart data={latencyData} />
          </div>

          {/* Throughput Timeline */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4">Throughput Timeline</h3>
            <ThroughputChart data={metricsHistory} />
          </div>
        </div>

        {/* System Resources */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4">CPU Usage</h3>
            <div className="flex items-center justify-center">
              <div className="relative w-32 h-32">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="#E5E7EB"
                    strokeWidth="8"
                    fill="none"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="#3B82F6"
                    strokeWidth="8"
                    fill="none"
                    strokeDasharray={`${(metrics.cpu_percent / 100) * 351.86} 351.86`}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-2xl font-bold">{metrics.cpu_percent?.toFixed(0)}%</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4">Memory Usage</h3>
            <div className="text-center">
              <span className="text-4xl font-bold text-purple-600">
                {metrics.memory_mb?.toFixed(0)}
              </span>
              <span className="text-lg text-gray-500 ml-1">MB</span>
            </div>
            <div className="mt-4 h-3 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-purple-500 transition-all duration-500"
                style={{ width: `${Math.min(metrics.memory_percent || 0, 100)}%` }}
              />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4">Connection Timeline</h3>
            <ConnectionChart data={metricsHistory} />
          </div>
        </div>

        {/* Test Controls */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Test Controls</h3>
          {currentTest?.progress && (
            <div className="mb-4 p-3 bg-blue-50 rounded-lg text-sm text-blue-800">
              {currentTest.progress}
            </div>
          )}
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => startTest({ name: 'quick_test', connections: 50, duration: 30 })}
              disabled={isRunning}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              Quick Test (50 conn)
            </button>
            <button
              onClick={() => startTest({ name: 'load_test', connections: 200, duration: 60 })}
              disabled={isRunning}
              className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              Load Test (200 conn)
            </button>
            <button
              onClick={() => startTest({ name: 'stress_test', connections: 500, duration: 60 })}
              disabled={isRunning}
              className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              Stress Test (500 conn)
            </button>
            <button
              onClick={stopTest}
              disabled={!isRunning}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              Stop Test
            </button>
          </div>
        </div>

        {/* Test Results */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4">Test History</h3>
          {testResults.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No test results yet</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Test</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Status</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">P99 Latency</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Throughput</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {testResults.slice().reverse().map((test, index) => (
                    <tr key={index} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium">{test.name}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          test.status === 'completed' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {test.status}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        {test.results?.p99_latency?.toFixed(2) || '-'} ms
                      </td>
                      <td className="py-3 px-4">
                        {test.results?.throughput?.toFixed(0) || '-'} msg/s
                      </td>
                      <td className="py-3 px-4 text-gray-500 text-sm">
                        {new Date(test.start_time).toLocaleTimeString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default React.memo(App);
