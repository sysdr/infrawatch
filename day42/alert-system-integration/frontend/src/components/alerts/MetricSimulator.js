import React, { useState } from 'react';
import { alertAPI } from '../../services/api';
import '../../styles/MetricSimulator.css';

function MetricSimulator() {
    const [metric, setMetric] = useState('cpu_usage');
    const [value, setValue] = useState(50);
    const [sending, setSending] = useState(false);
    const [message, setMessage] = useState('');

    const predefinedMetrics = [
        { name: 'cpu_usage', label: 'CPU Usage (%)', min: 0, max: 100 },
        { name: 'memory_usage', label: 'Memory Usage (%)', min: 0, max: 100 },
        { name: 'response_time_ms', label: 'Response Time (ms)', min: 0, max: 3000 },
    ];

    const currentMetric = predefinedMetrics.find(m => m.name === metric) || predefinedMetrics[0];

    const sendMetric = async () => {
        setSending(true);
        setMessage('');
        
        try {
            const metricData = [{
                metric: metric,
                value: parseFloat(value),
                timestamp: new Date().toISOString(),
                labels: {
                    source: 'simulator',
                    environment: 'test'
                }
            }];

            await alertAPI.ingestMetrics(metricData);
            setMessage(`✅ Sent ${metric}=${value}`);
            
            setTimeout(() => setMessage(''), 3000);
        } catch (error) {
            setMessage(`❌ Error: ${error.message}`);
        } finally {
            setSending(false);
        }
    };

    const sendBurst = async () => {
        setSending(true);
        setMessage('Sending burst...');
        
        try {
            const metrics = [];
            const burstValue = parseFloat(value);
            
            for (let i = 0; i < 5; i++) {
                metrics.push({
                    metric: metric,
                    value: burstValue + (Math.random() * 10 - 5),
                    timestamp: new Date(Date.now() + i * 1000).toISOString(),
                    labels: {
                        source: 'simulator',
                        environment: 'test'
                    }
                });
            }

            await alertAPI.ingestMetrics(metrics);
            setMessage(`✅ Sent burst of 5 metrics`);
            
            setTimeout(() => setMessage(''), 3000);
        } catch (error) {
            setMessage(`❌ Error: ${error.message}`);
        } finally {
            setSending(false);
        }
    };

    return (
        <div className="metric-simulator">
            <h2>📊 Metric Simulator</h2>
            <p className="simulator-description">
                Send test metrics to trigger alerts and observe real-time system behavior
            </p>

            <div className="simulator-controls">
                <div className="control-group">
                    <label>Metric Type</label>
                    <select 
                        value={metric} 
                        onChange={(e) => {
                            setMetric(e.target.value);
                            const newMetric = predefinedMetrics.find(m => m.name === e.target.value);
                            setValue(newMetric ? (newMetric.max / 2) : 50);
                        }}
                        disabled={sending}
                    >
                        {predefinedMetrics.map(m => (
                            <option key={m.name} value={m.name}>{m.label}</option>
                        ))}
                    </select>
                </div>

                <div className="control-group">
                    <label>
                        Value: {value}
                        {metric.includes('usage') && '%'}
                        {metric.includes('time') && 'ms'}
                    </label>
                    <input
                        type="range"
                        min={currentMetric.min}
                        max={currentMetric.max}
                        value={value}
                        onChange={(e) => setValue(e.target.value)}
                        disabled={sending}
                        className="value-slider"
                    />
                    <input
                        type="number"
                        min={currentMetric.min}
                        max={currentMetric.max}
                        value={value}
                        onChange={(e) => setValue(e.target.value)}
                        disabled={sending}
                        className="value-input"
                    />
                </div>

                <div className="button-group">
                    <button 
                        onClick={sendMetric}
                        disabled={sending}
                        className="btn btn-primary"
                    >
                        {sending ? 'Sending...' : 'Send Single Metric'}
                    </button>
                    <button 
                        onClick={sendBurst}
                        disabled={sending}
                        className="btn btn-secondary"
                    >
                        Send Burst (5 metrics)
                    </button>
                </div>

                {message && (
                    <div className={`simulator-message ${message.includes('✅') ? 'success' : 'error'}`}>
                        {message}
                    </div>
                )}
            </div>

            <div className="simulator-hints">
                <h3>💡 Tips</h3>
                <ul>
                    <li>Set CPU or Memory &gt; 80% to trigger warning alerts</li>
                    <li>Set CPU or Memory &gt; 90% to trigger critical alerts</li>
                    <li>Set Response Time &gt; 1000ms to trigger slow response alerts</li>
                    <li>Use burst mode to simulate sustained high values</li>
                    <li>Lower values to resolve alerts</li>
                </ul>
            </div>
        </div>
    );
}

export default MetricSimulator;
