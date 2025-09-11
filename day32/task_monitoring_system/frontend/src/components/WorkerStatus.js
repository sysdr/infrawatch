import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Server, Cpu, MemoryStick, Activity } from 'lucide-react';
import './WorkerStatus.css';

const WorkerStatus = () => {
  const [workers, setWorkers] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchWorkers();
    
    // Refresh every 10 seconds
    const interval = setInterval(fetchWorkers, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchWorkers = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/monitoring/workers/health');
      setWorkers(response.data.workers || []);
    } catch (error) {
      console.error('Error fetching workers:', error);
    } finally {
      setLoading(false);
    }
  };

  const registerDemoWorker = async () => {
    try {
      const workerId = `demo-worker-${Date.now()}`;
      await axios.post('/api/workers/register', {
        worker_id: workerId,
        name: `Demo Worker ${workerId.slice(-6)}`,
        host: 'localhost',
        port: Math.floor(Math.random() * 1000) + 8000
      });
      
      // Send initial heartbeat
      await axios.post(`/api/workers/${workerId}/heartbeat`, {
        worker_id: workerId,
        cpu_usage: Math.random() * 100,
        memory_usage: Math.random() * 100,
        task_count: Math.floor(Math.random() * 10),
        is_healthy: true
      });
      
      fetchWorkers();
    } catch (error) {
      console.error('Error registering demo worker:', error);
    }
  };

  const getHealthStatus = (worker) => {
    if (!worker.is_healthy) return 'unhealthy';
    
    const timeSinceHeartbeat = new Date() - new Date(worker.last_heartbeat);
    if (timeSinceHeartbeat > 5 * 60 * 1000) return 'stale'; // 5 minutes
    
    return 'healthy';
  };

  const getHealthColor = (status) => {
    switch (status) {
      case 'healthy': return '#10b981';
      case 'stale': return '#f59e0b';
      case 'unhealthy': return '#ef4444';
      default: return '#6b7280';
    }
  };

  return (
    <div className="worker-status-container">
      <div className="worker-header">
        <h2>Worker Management</h2>
        <div className="header-actions">
          <button onClick={registerDemoWorker} className="register-btn">
            Register Demo Worker
          </button>
          <button onClick={fetchWorkers} className="refresh-btn">
            Refresh
          </button>
        </div>
      </div>
      
      {/* Worker Summary */}
      <div className="worker-summary">
        <div className="summary-card">
          <div className="summary-icon">
            <Server />
          </div>
          <div className="summary-content">
            <h3>Total Workers</h3>
            <div className="summary-value">{workers.length}</div>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon healthy">
            <Activity />
          </div>
          <div className="summary-content">
            <h3>Healthy Workers</h3>
            <div className="summary-value">
              {workers.filter(w => getHealthStatus(w) === 'healthy').length}
            </div>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon unhealthy">
            <Activity />
          </div>
          <div className="summary-content">
            <h3>Unhealthy Workers</h3>
            <div className="summary-value">
              {workers.filter(w => getHealthStatus(w) === 'unhealthy').length}
            </div>
          </div>
        </div>
      </div>
      
      {/* Worker List */}
      <div className="worker-list">
        {loading ? (
          <div className="loading">Loading workers...</div>
        ) : workers.length === 0 ? (
          <div className="empty-state">
            <Server size={48} />
            <p>No workers registered</p>
            <button onClick={registerDemoWorker} className="register-btn">
              Register Demo Worker
            </button>
          </div>
        ) : (
          <div className="worker-grid">
            {workers.map(worker => {
              const healthStatus = getHealthStatus(worker);
              const healthColor = getHealthColor(healthStatus);
              
              return (
                <div key={worker.id} className="worker-card">
                  <div className="worker-header">
                    <div className="worker-info">
                      <h3>{worker.name}</h3>
                      <span className="worker-id">{worker.id}</span>
                    </div>
                    <div 
                      className="health-indicator"
                      style={{ backgroundColor: healthColor }}
                    >
                      {healthStatus}
                    </div>
                  </div>
                  
                  <div className="worker-details">
                    <div className="detail-row">
                      <span>Host:</span>
                      <span>{worker.host}:{worker.port}</span>
                    </div>
                    
                    <div className="detail-row">
                      <span>Status:</span>
                      <span>{worker.status}</span>
                    </div>
                    
                    <div className="detail-row">
                      <span>Tasks:</span>
                      <span>{worker.task_count}</span>
                    </div>
                    
                    <div className="detail-row">
                      <span>Last Heartbeat:</span>
                      <span>{new Date(worker.last_heartbeat).toLocaleString()}</span>
                    </div>
                  </div>
                  
                  <div className="resource-usage">
                    <div className="resource-item">
                      <div className="resource-header">
                        <Cpu size={16} />
                        <span>CPU Usage</span>
                        <span>{worker.cpu_usage.toFixed(1)}%</span>
                      </div>
                      <div className="resource-bar">
                        <div 
                          className="resource-fill"
                          style={{ width: `${worker.cpu_usage}%` }}
                        />
                      </div>
                    </div>
                    
                    <div className="resource-item">
                      <div className="resource-header">
                        <MemoryStick size={16} />
                        <span>Memory Usage</span>
                        <span>{worker.memory_usage.toFixed(1)}%</span>
                      </div>
                      <div className="resource-bar">
                        <div 
                          className="resource-fill"
                          style={{ width: `${worker.memory_usage}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkerStatus;
