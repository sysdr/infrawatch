import React, { useState, useEffect } from 'react';
import { metricsAPI } from '../../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './PerformanceMonitor.css';

const PerformanceMonitor = ({ metricId }) => {
    const [performance, setPerformance] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadPerformance();
    }, [metricId]);

    const loadPerformance = async () => {
        try {
            const data = await metricsAPI.getPerformance(metricId);
            setPerformance(data);
        } catch (error) {
            console.error('Failed to load performance:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="loading">Loading performance data...</div>;
    }

    if (!performance) {
        return <div className="no-data">No performance data available</div>;
    }

    const chartData = [
        { name: 'Min', value: performance.min_execution_time_ms },
        { name: 'Avg', value: performance.avg_execution_time_ms },
        { name: 'Max', value: performance.max_execution_time_ms },
    ];

    return (
        <div className="performance-monitor">
            <h3>Performance Metrics: {performance.metric_name}</h3>
            
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-label">Total Executions</div>
                    <div className="stat-value">{performance.total_executions}</div>
                </div>
                
                <div className="stat-card">
                    <div className="stat-label">Success Rate</div>
                    <div className="stat-value">{performance.success_rate}%</div>
                </div>
                
                <div className="stat-card">
                    <div className="stat-label">Failed Executions</div>
                    <div className="stat-value error">{performance.failed_executions}</div>
                </div>
                
                <div className="stat-card">
                    <div className="stat-label">Avg Execution Time</div>
                    <div className="stat-value">{performance.avg_execution_time_ms.toFixed(2)} ms</div>
                </div>
            </div>

            <div className="chart-container">
                <h4>Execution Time Distribution</h4>
                <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis label={{ value: 'Time (ms)', angle: -90, position: 'insideLeft' }} />
                        <Tooltip />
                        <Bar dataKey="value" fill="#4CAF50" />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default PerformanceMonitor;
