import React, { useState, useEffect } from 'react';
import { metricsAPI } from './services/api';
import MetricBuilder from './components/MetricBuilder/MetricBuilder';
import PerformanceMonitor from './components/PerformanceMonitor/PerformanceMonitor';
import { Calculator, TrendingUp, AlertCircle } from 'lucide-react';
import './App.css';

function App() {
    const [metrics, setMetrics] = useState([]);
    const [selectedMetric, setSelectedMetric] = useState(null);
    const [calculationInputs, setCalculationInputs] = useState({});
    const [calculationResult, setCalculationResult] = useState(null);
    const [activeTab, setActiveTab] = useState('builder');

    useEffect(() => {
        loadMetrics();
    }, []);

    const loadMetrics = async () => {
        try {
            const data = await metricsAPI.listMetrics();
            setMetrics(data);
        } catch (error) {
            console.error('Failed to load metrics:', error);
        }
    };

    const handleMetricCreated = (metric) => {
        loadMetrics();
        setActiveTab('calculator');
    };

    const handleCalculate = async () => {
        if (!selectedMetric) return;

        try {
            const result = await metricsAPI.calculateMetric(
                selectedMetric.id,
                calculationInputs
            );
            setCalculationResult(result);
        } catch (error) {
            console.error('Calculation failed:', error);
            alert(error.response?.data?.detail || 'Calculation failed');
        }
    };

    const handleInputChange = (variable, value) => {
        setCalculationInputs(prev => ({
            ...prev,
            [variable]: parseFloat(value) || 0
        }));
    };

    return (
        <div className="app">
            <header className="app-header">
                <div className="header-content">
                    <h1><Calculator size={32} /> Custom Metrics Engine</h1>
                    <p>Define, calculate, and monitor custom business metrics</p>
                </div>
            </header>

            <div className="tabs">
                <button
                    className={`tab ${activeTab === 'builder' ? 'active' : ''}`}
                    onClick={() => setActiveTab('builder')}
                >
                    Create Metric
                </button>
                <button
                    className={`tab ${activeTab === 'calculator' ? 'active' : ''}`}
                    onClick={() => setActiveTab('calculator')}
                >
                    Calculate
                </button>
                <button
                    className={`tab ${activeTab === 'performance' ? 'active' : ''}`}
                    onClick={() => setActiveTab('performance')}
                >
                    Performance
                </button>
            </div>

            <main className="app-main">
                {activeTab === 'builder' && (
                    <MetricBuilder onMetricCreated={handleMetricCreated} />
                )}

                {activeTab === 'calculator' && (
                    <div className="calculator-section">
                        <div className="metric-selector">
                            <h2>Calculate Metric</h2>
                            <select
                                value={selectedMetric?.id || ''}
                                onChange={(e) => {
                                    const metric = metrics.find(m => m.id === e.target.value);
                                    setSelectedMetric(metric);
                                    setCalculationInputs({});
                                    setCalculationResult(null);
                                }}
                                className="metric-select"
                            >
                                <option value="">Select a metric...</option>
                                {metrics.map(metric => (
                                    <option key={metric.id} value={metric.id}>
                                        {metric.display_name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {selectedMetric && (
                            <div className="calculation-panel">
                                <div className="metric-info">
                                    <h3>{selectedMetric.display_name}</h3>
                                    <p className="formula-display">Formula: {selectedMetric.formula}</p>
                                    <p className="description">{selectedMetric.description}</p>
                                </div>

                                <div className="input-section">
                                    <h4>Input Values</h4>
                                    {selectedMetric.variables.map(variable => (
                                        <div key={variable} className="input-group">
                                            <label>{variable}</label>
                                            <input
                                                type="number"
                                                step="any"
                                                value={calculationInputs[variable] || ''}
                                                onChange={(e) => handleInputChange(variable, e.target.value)}
                                                placeholder={`Enter ${variable}`}
                                            />
                                        </div>
                                    ))}
                                    
                                    <button
                                        onClick={handleCalculate}
                                        className="calculate-btn"
                                        disabled={!Object.keys(calculationInputs).length}
                                    >
                                        Calculate
                                    </button>
                                </div>

                                {calculationResult && (
                                    <div className="result-panel">
                                        <div className="result-header">
                                            <TrendingUp size={24} />
                                            <h4>Result</h4>
                                        </div>
                                        <div className="result-value">
                                            {calculationResult.calculated_value.toFixed(2)}
                                            {selectedMetric.unit && ` ${selectedMetric.unit}`}
                                        </div>
                                        <div className="result-meta">
                                            <span>Execution time: {calculationResult.execution_time_ms.toFixed(2)} ms</span>
                                            <span className="success">✓ {calculationResult.status}</span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'performance' && (
                    <div className="performance-section">
                        <div className="metric-selector">
                            <h2>Performance Monitor</h2>
                            <select
                                value={selectedMetric?.id || ''}
                                onChange={(e) => {
                                    const metric = metrics.find(m => m.id === e.target.value);
                                    setSelectedMetric(metric);
                                }}
                                className="metric-select"
                            >
                                <option value="">Select a metric...</option>
                                {metrics.map(metric => (
                                    <option key={metric.id} value={metric.id}>
                                        {metric.display_name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {selectedMetric && (
                            <PerformanceMonitor metricId={selectedMetric.id} />
                        )}
                    </div>
                )}
            </main>
        </div>
    );
}

export default App;
