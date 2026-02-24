import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { useWebSocket } from './hooks/useWebSocket';
import { TestControls } from './components/TestControls';
import { LiveCharts } from './components/LiveCharts';
import { BenchmarkTable } from './components/BenchmarkTable';
import { RunHistory } from './components/RunHistory';
import { GaugeChart } from './components/GaugeChart';

const API = 'http://localhost:8117';

export default function App() {
  const [activeRunId, setActiveRunId] = useState(null);
  const [activeRunType, setActiveRunType] = useState('load');
  const [runStatus, setRunStatus] = useState('idle');
  const [benchmarks, setBenchmarks] = useState([]);
  const [stressResult, setStressResult] = useState(null);
  const [systemMetrics, setSystemMetrics] = useState({ cpu_percent: 0, memory_percent: 0 });
  const [errorRate, setErrorRate] = useState(0);
  const [currentRPS, setCurrentRPS] = useState(0);
  const [refreshKey, setRefreshKey] = useState(0);

  const wsUrl = activeRunId ? `ws://localhost:8117/api/tests/ws/${activeRunId}` : null;
  const { messages, connected } = useWebSocket(wsUrl);

  // Process incoming WS messages
  useEffect(() => {
    if (!messages.length) return;
    const last = messages[messages.length - 1];

    if (last.type === 'metric') {
      setSystemMetrics({ cpu_percent: last.cpu_percent || 0, memory_percent: last.memory_percent || 0 });
      setErrorRate(last.error_rate || 0);
      setCurrentRPS(last.rps || 0);
      setRunStatus('running');
    }
    if (last.type === 'completed') {
      setRunStatus('completed');
      setRefreshKey(k => k + 1);
    }
    if (last.type === 'benchmark_completed') {
      setBenchmarks(last.benchmarks || []);
      setRunStatus('completed');
      setRefreshKey(k => k + 1);
    }
    if (last.type === 'stress_completed') {
      setStressResult(last);
      setRunStatus('completed');
      setRefreshKey(k => k + 1);
    }
    if (last.type === 'stress_probe') {
      setCurrentRPS(last.probed_rps || 0);
      setErrorRate(last.error_rate || 0);
    }
  }, [messages]);

  // Poll system metrics independently
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const r = await axios.get(`${API}/api/system/metrics`);
        if (runStatus !== 'running') {
          setSystemMetrics({ cpu_percent: r.data.cpu_percent, memory_percent: r.data.memory_percent });
        }
      } catch {}
    }, 3000);
    return () => clearInterval(interval);
  }, [runStatus]);

  const handleRunStarted = useCallback((runId, testType) => {
    setActiveRunId(runId);
    setActiveRunType(testType);
    setRunStatus('starting');
    setBenchmarks([]);
    setStressResult(null);
  }, []);

  const statusDot = { running: '#4caf50', starting: '#ff9800', completed: '#2196f3', idle: '#64748b' }[runStatus] || '#64748b';

  return (
    <div style={{ minHeight: '100vh', background: '#0f172a', fontFamily: "'Inter', 'Segoe UI', sans-serif" }}>
      {/* Header */}
      <div style={{ background: '#1e293b', borderBottom: '1px solid #334155', padding: '0 24px' }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto', height: '56px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '28px', height: '28px', background: 'linear-gradient(135deg, #2e7d32, #66bb6a)',
              borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '14px', fontWeight: '700', color: '#fff' }}>
              LT
            </div>
            <span style={{ color: '#e2e8f0', fontSize: '15px', fontWeight: '700' }}>LoadTest Platform</span>
            <span style={{ color: '#334155', fontSize: '13px' }}>|</span>
            <span style={{ color: '#64748b', fontSize: '12px' }}>Day 117 · Infrastructure Management</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ width: '7px', height: '7px', borderRadius: '50%', background: statusDot }} />
              <span style={{ color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase',
                letterSpacing: '0.05em', fontWeight: '600' }}>
                {runStatus}
              </span>
            </div>
            {connected && activeRunId && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <div style={{ width: '7px', height: '7px', borderRadius: '50%', background: '#4caf50',
                  animation: 'pulse 2s infinite' }} />
                <span style={{ color: '#4caf50', fontSize: '11px' }}>LIVE</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '24px' }}>
        {/* Top row: KPI cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
          {[
            { label: 'Current RPS', value: Math.round(currentRPS), unit: 'req/s', color: '#4caf50' },
            { label: 'Error Rate', value: errorRate.toFixed(1), unit: '%', color: errorRate > 5 ? '#f44336' : '#4caf50' },
            { label: 'Active Run', value: activeRunId ? activeRunId.slice(0, 8) : '—', unit: '', color: '#2196f3' },
            { label: 'Test Type', value: activeRunType.toUpperCase(), unit: '', color: '#ff9800' },
          ].map(kpi => (
            <div key={kpi.label} style={{ background: '#1e293b', borderRadius: '10px', padding: '16px 20px',
              border: '1px solid #334155' }}>
              <div style={{ color: '#64748b', fontSize: '10px', fontWeight: '600',
                textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>
                {kpi.label}
              </div>
              <div style={{ color: kpi.color, fontSize: '22px', fontWeight: '700', fontVariantNumeric: 'tabular-nums' }}>
                {kpi.value}<span style={{ fontSize: '12px', color: '#64748b', marginLeft: '4px' }}>{kpi.unit}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Main grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: '20px', marginBottom: '24px' }}>
          {/* Left: controls + gauges */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <TestControls onRunStarted={handleRunStarted} />
            <div style={{ background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '16px' }}>
              <div style={{ color: '#94a3b8', fontSize: '11px', fontWeight: '600',
                textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>
                Resource Monitor
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <GaugeChart value={systemMetrics.cpu_percent} label="CPU" />
                <GaugeChart value={systemMetrics.memory_percent} label="Memory" />
              </div>
            </div>
          </div>

          {/* Right: live charts */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <LiveCharts messages={messages} />

            {/* Stress result card */}
            {stressResult && (
              <div style={{ background: '#1e293b', borderRadius: '12px', border: '1px solid #ff9800',
                padding: '20px' }}>
                <div style={{ color: '#ff9800', fontSize: '11px', fontWeight: '600',
                  textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '16px' }}>
                  ⚡ Stress Test Result
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                  {[
                    { label: 'Max Sustainable RPS', value: stressResult.max_rps_sustainable, unit: 'rps', color: '#4caf50' },
                    { label: 'Breakdown RPS', value: stressResult.breakdown_rps, unit: 'rps', color: '#f44336' },
                    { label: 'Error Threshold', value: stressResult.error_threshold_percent, unit: '%', color: '#ff9800' },
                  ].map(m => (
                    <div key={m.label} style={{ textAlign: 'center' }}>
                      <div style={{ color: m.color, fontSize: '28px', fontWeight: '700' }}>
                        {m.value}<span style={{ fontSize: '12px', marginLeft: '4px' }}>{m.unit}</span>
                      </div>
                      <div style={{ color: '#64748b', fontSize: '11px', marginTop: '4px' }}>{m.label}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Benchmark table */}
        <div style={{ marginBottom: '20px' }}>
          <BenchmarkTable benchmarks={benchmarks} />
        </div>

        {/* Run history */}
        <RunHistory refreshKey={refreshKey} />
      </div>

      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0f172a; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
        select option { background: #1e293b; }
      `}</style>
    </div>
  );
}
