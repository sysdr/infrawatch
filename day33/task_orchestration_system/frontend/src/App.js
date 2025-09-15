import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import WorkflowList from './components/WorkflowList';
import WorkflowDetail from './components/WorkflowDetail';
import Metrics from './components/Metrics';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [workflows, setWorkflows] = useState([]);
  const [metrics, setMetrics] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchWorkflows();
    fetchMetrics();
    
    // Set up real-time updates
    const interval = setInterval(() => {
      fetchWorkflows();
      fetchMetrics();
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const fetchWorkflows = async () => {
    try {
      const response = await axios.get('/api/v1/workflows');
      setWorkflows(response.data.workflows);
    } catch (error) {
      console.error('Error fetching workflows:', error);
    }
  };

  const fetchMetrics = async () => {
    try {
      const response = await axios.get('/api/v1/metrics');
      setMetrics(response.data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  const createSampleWorkflow = async (type) => {
    setLoading(true);
    try {
      const response = await axios.post(`/api/v1/workflows/samples/${type}`);
      console.log(`Created ${type} workflow:`, response.data);
      fetchWorkflows();
    } catch (error) {
      console.error(`Error creating ${type} workflow:`, error);
    } finally {
      setLoading(false);
    }
  };

  const executeWorkflow = async (workflowId) => {
    try {
      await axios.post(`/api/v1/workflows/${workflowId}/execute`);
      console.log(`Executing workflow: ${workflowId}`);
    } catch (error) {
      console.error('Error executing workflow:', error);
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <Dashboard 
            workflows={workflows}
            metrics={metrics}
            onCreateSample={createSampleWorkflow}
            onExecuteWorkflow={executeWorkflow}
            loading={loading}
          />
        );
      case 'workflows':
        return selectedWorkflow ? (
          <WorkflowDetail 
            workflow={selectedWorkflow}
            onBack={() => setSelectedWorkflow(null)}
            onExecute={executeWorkflow}
          />
        ) : (
          <WorkflowList 
            workflows={workflows}
            onSelectWorkflow={setSelectedWorkflow}
            onExecuteWorkflow={executeWorkflow}
          />
        );
      case 'metrics':
        return <Metrics metrics={metrics} />;
      default:
        return <Dashboard workflows={workflows} metrics={metrics} />;
    }
  };

  return (
    <div className="App">
      <div className="wp-admin-bar">
        <span className="real-time-indicator"></span>
        Task Orchestration System - Live Dashboard
      </div>
      
      <div className="wp-header">
        <h1>Advanced Task Patterns</h1>
      </div>

      <nav className="wp-nav">
        <ul>
          <li>
            <a 
              href="#dashboard"
              className={activeTab === 'dashboard' ? 'active' : ''}
              onClick={(e) => { e.preventDefault(); setActiveTab('dashboard'); setSelectedWorkflow(null); }}
            >
              📊 Dashboard
            </a>
          </li>
          <li>
            <a 
              href="#workflows"
              className={activeTab === 'workflows' ? 'active' : ''}
              onClick={(e) => { e.preventDefault(); setActiveTab('workflows'); }}
            >
              🔄 Workflows
            </a>
          </li>
          <li>
            <a 
              href="#metrics"
              className={activeTab === 'metrics' ? 'active' : ''}
              onClick={(e) => { e.preventDefault(); setActiveTab('metrics'); }}
            >
              📈 Metrics
            </a>
          </li>
        </ul>
      </nav>

      <main className="wp-main">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;
