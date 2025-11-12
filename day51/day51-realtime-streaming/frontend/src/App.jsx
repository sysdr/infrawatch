import React, { useState, useEffect } from 'react'
import { useWebSocket } from './hooks/useWebSocket'
import MetricsChart from './components/MetricsChart'
import AlertPanel from './components/AlertPanel'
import ConnectionStatus from './components/ConnectionStatus'
import StatsPanel from './components/StatsPanel'
import './styles/App.css'

function App() {
  const { 
    connected, 
    metrics, 
    alerts, 
    stats,
    subscribe,
    unsubscribe 
  } = useWebSocket('http://localhost:8000')

  useEffect(() => {
    if (connected) {
      subscribe(['metrics_update', 'alerts_critical', 'alerts_warning'])
    }
  }, [connected])

  return (
    <div className="app">
      <header className="app-header">
        <h1>Real-time Streaming Dashboard</h1>
        <ConnectionStatus connected={connected} />
      </header>

      <main className="app-main">
        <div className="grid-container">
          <div className="grid-item full-width">
            <AlertPanel alerts={alerts} />
          </div>

          <div className="grid-item">
            <MetricsChart 
              title="CPU Usage" 
              data={metrics} 
              dataKey="cpu.percent"
              color="#3b82f6"
              unit="%"
            />
          </div>

          <div className="grid-item">
            <MetricsChart 
              title="Memory Usage" 
              data={metrics} 
              dataKey="memory.percent"
              color="#10b981"
              unit="%"
            />
          </div>

          <div className="grid-item">
            <MetricsChart 
              title="Disk Usage" 
              data={metrics} 
              dataKey="disk.percent"
              color="#f59e0b"
              unit="%"
            />
          </div>

          <div className="grid-item">
            <StatsPanel stats={stats} metricsCount={metrics.length} />
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
