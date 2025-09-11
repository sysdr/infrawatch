import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import axios from 'axios';
import './MetricsChart.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const MetricsChart = ({ socket }) => {
  const [metricsHistory, setMetricsHistory] = useState([]);
  const [currentMetrics, setCurrentMetrics] = useState({});
  const [chartType, setChartType] = useState('tasks');

  useEffect(() => {
    // Fetch initial metrics
    fetchMetrics();
    
    // WebSocket listener for real-time updates
    if (socket) {
      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setCurrentMetrics(data);
          
          // Add to history (keep last 20 points)
          setMetricsHistory(prev => {
            const newHistory = [...prev, {
              ...data,
              timestamp: new Date().toLocaleTimeString()
            }];
            return newHistory.slice(-20);
          });
        } catch (error) {
          console.error('Error parsing metrics:', error);
        }
      };
    }
  }, [socket]);

  const fetchMetrics = async () => {
    try {
      const response = await axios.get('/api/monitoring/metrics');
      const data = response.data;
      
      setCurrentMetrics(data);
      setMetricsHistory(prev => {
        const newHistory = [...prev, {
          ...data,
          timestamp: new Date().toLocaleTimeString()
        }];
        return newHistory.slice(-20);
      });
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  // Task Status Chart Data
  const taskStatusData = {
    labels: ['Queued', 'Processing', 'Completed', 'Failed'],
    datasets: [
      {
        data: [
          currentMetrics.tasks?.queued || 0,
          currentMetrics.tasks?.processing || 0,
          currentMetrics.tasks?.completed || 0,
          currentMetrics.tasks?.failed || 0
        ],
        backgroundColor: [
          '#fbbf24',
          '#3b82f6',
          '#10b981',
          '#ef4444'
        ],
        borderWidth: 2,
        borderColor: '#fff'
      }
    ]
  };

  // System Resource Chart Data
  const systemResourceData = {
    labels: metricsHistory.map(m => m.timestamp),
    datasets: [
      {
        label: 'CPU Usage (%)',
        data: metricsHistory.map(m => m.system?.cpu_usage || 0),
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Memory Usage (%)',
        data: metricsHistory.map(m => m.system?.memory_usage || 0),
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      }
    ]
  };

  // Task Throughput Chart Data
  const throughputData = {
    labels: metricsHistory.map(m => m.timestamp),
    datasets: [
      {
        label: 'Tasks Completed',
        data: metricsHistory.map(m => m.tasks?.completed || 0),
        backgroundColor: '#10b981',
        borderColor: '#059669',
        borderWidth: 2,
      },
      {
        label: 'Tasks Failed',
        data: metricsHistory.map(m => m.tasks?.failed || 0),
        backgroundColor: '#ef4444',
        borderColor: '#dc2626',
        borderWidth: 2,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      }
    },
  };

  const doughnutOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
      },
    },
  };

  return (
    <div className="metrics-container">
      <div className="metrics-header">
        <h2>System Metrics</h2>
        <div className="chart-selector">
          <button 
            className={chartType === 'tasks' ? 'active' : ''}
            onClick={() => setChartType('tasks')}
          >
            Task Status
          </button>
          <button 
            className={chartType === 'system' ? 'active' : ''}
            onClick={() => setChartType('system')}
          >
            System Resources
          </button>
          <button 
            className={chartType === 'throughput' ? 'active' : ''}
            onClick={() => setChartType('throughput')}
          >
            Throughput
          </button>
        </div>
      </div>
      
      <div className="metrics-content">
        {/* Current Stats */}
        <div className="current-stats">
          <div className="stat-item">
            <h4>Current Load</h4>
            <div className="stat-value">
              {(currentMetrics.tasks?.processing || 0) + (currentMetrics.tasks?.queued || 0)}
            </div>
            <div className="stat-label">Active + Queued Tasks</div>
          </div>
          
          <div className="stat-item">
            <h4>Avg Execution Time</h4>
            <div className="stat-value">
              {currentMetrics.performance?.avg_execution_time?.toFixed(2) || '0.00'}s
            </div>
            <div className="stat-label">Last Hour Average</div>
          </div>
          
          <div className="stat-item">
            <h4>Throughput</h4>
            <div className="stat-value">
              {currentMetrics.performance?.throughput_per_hour || 0}
            </div>
            <div className="stat-label">Tasks/Hour</div>
          </div>
          
          <div className="stat-item">
            <h4>System Health</h4>
            <div className="stat-value">
              {currentMetrics.system?.cpu_usage < 80 && 
               currentMetrics.system?.memory_usage < 80 ? '✅' : '⚠️'}
            </div>
            <div className="stat-label">
              CPU: {currentMetrics.system?.cpu_usage?.toFixed(1) || 0}%
            </div>
          </div>
        </div>
        
        {/* Chart Display */}
        <div className="chart-container">
          {chartType === 'tasks' && (
            <div className="chart-wrapper">
              <h3>Task Status Distribution</h3>
              <div className="chart-content">
                <Doughnut data={taskStatusData} options={doughnutOptions} />
              </div>
            </div>
          )}
          
          {chartType === 'system' && (
            <div className="chart-wrapper">
              <h3>System Resource Usage Over Time</h3>
              <div className="chart-content">
                <Line data={systemResourceData} options={chartOptions} />
              </div>
            </div>
          )}
          
          {chartType === 'throughput' && (
            <div className="chart-wrapper">
              <h3>Task Throughput History</h3>
              <div className="chart-content">
                <Bar data={throughputData} options={chartOptions} />
              </div>
            </div>
          )}
        </div>
        
        {/* Queue Status */}
        <div className="queue-status">
          <h3>Queue Status</h3>
          <div className="queue-list">
            {Object.entries(currentMetrics.queues || {}).map(([queueName, depth]) => (
              <div key={queueName} className="queue-item">
                <div className="queue-name">{queueName}</div>
                <div className="queue-depth">{depth} tasks</div>
                <div className="queue-bar">
                  <div 
                    className="queue-fill"
                    style={{ 
                      width: `${Math.min(depth / 10 * 100, 100)}%`,
                      backgroundColor: depth > 50 ? '#ef4444' : depth > 20 ? '#f59e0b' : '#10b981'
                    }}
                  />
                </div>
              </div>
            ))}
            
            {Object.keys(currentMetrics.queues || {}).length === 0 && (
              <div className="empty-queues">No active queues</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetricsChart;
