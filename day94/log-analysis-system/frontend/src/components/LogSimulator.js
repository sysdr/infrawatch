import React, { useState } from 'react';
import axios from 'axios';

function LogSimulator() {
  const [isSimulating, setIsSimulating] = useState(false);
  const [logCount, setLogCount] = useState(0);
  const [simulationType, setSimulationType] = useState('normal');

  const sampleLogs = {
    normal: [
      { message: "User 12345 logged in successfully from IP 192.168.1.100", level: "INFO", metrics: { response_time: 45, error_rate: 0.1 } },
      { message: "API request processed in 23ms", level: "INFO", metrics: { response_time: 23, error_rate: 0.1 } },
      { message: "Database query executed successfully", level: "INFO", metrics: { response_time: 34, error_rate: 0.1 } },
    ],
    errors: [
      { message: "Failed to connect to database timeout after 30s", level: "ERROR", metrics: { response_time: 30000, error_rate: 15 } },
      { message: "Authentication failed for user 98765", level: "ERROR", metrics: { response_time: 67, error_rate: 12 } },
      { message: "Critical service unavailable", level: "CRITICAL", metrics: { response_time: 5000, error_rate: 20 } },
    ],
    anomaly: [
      { message: "Request processed", level: "INFO", metrics: { response_time: 5000, error_rate: 25 } },
      { message: "Unusual traffic pattern detected", level: "WARN", metrics: { response_time: 3456, error_rate: 18 } },
    ]
  };

  const simulateLogs = async () => {
    setIsSimulating(true);
    setLogCount(0);

    const logs = sampleLogs[simulationType];
    const iterations = simulationType === 'normal' ? 50 : 20;

    for (let i = 0; i < iterations; i++) {
      const log = logs[Math.floor(Math.random() * logs.length)];
      
      try {
        await axios.post('http://localhost:8000/api/logs/analyze', {
          ...log,
          source: 'simulator',
          timestamp: new Date().toISOString()
        });
        setLogCount(prev => prev + 1);
      } catch (error) {
        console.error('Error sending log:', error);
      }

      await new Promise(resolve => setTimeout(resolve, 200));
    }

    setIsSimulating(false);
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>🎮 Log Simulator</h2>
      </div>

      <div style={{maxWidth: '600px', margin: '0 auto'}}>
        <div style={{marginBottom: '2rem'}}>
          <h3>Simulation Type:</h3>
          <div style={{display: 'flex', gap: '1rem', marginTop: '1rem'}}>
            <label style={{flex: 1, padding: '1rem', border: '2px solid #e5e7eb', borderRadius: '8px', cursor: 'pointer'}}>
              <input 
                type="radio" 
                name="simType" 
                value="normal"
                checked={simulationType === 'normal'}
                onChange={(e) => setSimulationType(e.target.value)}
              />
              {' '}Normal Operations
            </label>
            <label style={{flex: 1, padding: '1rem', border: '2px solid #e5e7eb', borderRadius: '8px', cursor: 'pointer'}}>
              <input 
                type="radio" 
                name="simType" 
                value="errors"
                checked={simulationType === 'errors'}
                onChange={(e) => setSimulationType(e.target.value)}
              />
              {' '}Error Scenarios
            </label>
            <label style={{flex: 1, padding: '1rem', border: '2px solid #e5e7eb', borderRadius: '8px', cursor: 'pointer'}}>
              <input 
                type="radio" 
                name="simType" 
                value="anomaly"
                checked={simulationType === 'anomaly'}
                onChange={(e) => setSimulationType(e.target.value)}
              />
              {' '}Anomalies
            </label>
          </div>
        </div>

        <button 
          className="refresh-button"
          onClick={simulateLogs}
          disabled={isSimulating}
          style={{
            width: '100%',
            padding: '1rem',
            fontSize: '1.1rem',
            opacity: isSimulating ? 0.6 : 1
          }}
        >
          {isSimulating ? `Simulating... (${logCount} logs)` : '▶️ Start Simulation'}
        </button>

        <div style={{marginTop: '2rem', padding: '1.5rem', background: '#f9fafb', borderRadius: '8px'}}>
          <h3>Instructions:</h3>
          <ol style={{marginLeft: '1.5rem', marginTop: '1rem'}}>
            <li>Select a simulation type above</li>
            <li>Click "Start Simulation" to generate logs</li>
            <li>Switch to other tabs to see analysis results</li>
            <li>Watch patterns, anomalies, and alerts update in real-time</li>
          </ol>
        </div>
      </div>
    </div>
  );
}

export default LogSimulator;
